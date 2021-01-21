# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
import logging
import re

import flask

from bs4 import BeautifulSoup

from shared import auth_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.service import Service
from shared.datastore.user import User
from shared.exceptions import SyncException
from shared.services.google.client import create_gmail_client

import sync_helper


module = flask.Blueprint('google', __name__)

SUBJECT_REGEX = re.compile(r"Watch (?P<name>.*)'s live activity now!")


@module.route('/pubsub/rides', methods=['POST'])
def pubsub_rides():
    auth_util.verify(flask.request)
    if flask.request.args.get('token', '') != config.pubsub_creds['token']:
        return responses.INVALID_TOKEN

    envelope = json.loads(flask.request.data)
    payload = json.loads(base64.b64decode(envelope['message']['data']))
    logging.debug('Received Payload: %s', payload)

    uid = auth_util.get_uid_by_email(payload['emailAddress'])
    user = User.from_uid(uid)

    task_util.process_pubsub_rides(user, payload)

    return responses.OK


@module.route('/process/rides', methods=['POST'])
def pubsub_process_rides():
    auth_util.verify(flask.request)
    params = task_util.get_payload(flask.request)
    service = Service.get('google', params['user'].key)
    payload = params['payload']
    logging.info('process_pubsub_rides: %s -> %s', payload['emailAddress'], service.key)

    try:
        sync_helper.do(
            PubsubWorker(service, payload),
            work_key='%s/%s' % (payload['emailAddress'], payload['historyId']),
        )
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


class Worker(object):
    def __init__(self, service):
        self.service = service
        self.client = create_gmail_client(service)

    def sync(self):
        request = {
            'labelIds': ['INBOX'],
            'topicName': 'projects/%s/topics/rides' % (config.project_id,),
        }
        watch = self.client.users().watch(userId='me', body=request).execute()
        logging.debug('Watching: %s -> %s', self.service.key, watch)


class PubsubWorker(object):
    def __init__(self, service, payload):
        self.service = service
        self.payload = payload
        self.client = create_gmail_client(service)

    def sync(self):
        request = (
            self.client.users()
            .history()
            .list(
                userId='me',
                labelId='INBOX',
                historyTypes=['messageAdded'],
                startHistoryId=self.payload['historyId'],
            )
        )
        messages = set()
        logging.debug('Fetching history')
        while request is not None:
            response = request.execute()
            for h in response.get('history', []):
                for m in h.get('messages', []):
                    messages.add(m['id'])
            request = self.client.users().history().list_next(request, response)

        logging.debug('Fetching messages: %s', messages)
        for m in messages:
            request = (
                self.client.users().messages().get(userId='me', id=m, format='full')
            )
            response = request.execute()
            garmin_url = self._extract_garmin_url(m, response)
            if garmin_url is not None:
                task_util.process_garmin_livetrack(garmin_url)
                continue
        return responses.OK

    def _extract_garmin_url(self, m, response):
        logging.debug('Extracting Garmin URL: %s: %s', m)
        headers = dict(
            [
                (header['name'], header['value'])
                for header in response['payload']['headers']
                if header['name'] in ('From', 'To', 'Subject')
            ]
        )
        logging.debug('Fetched message: %s', m)
        if headers.get('From') != 'Garmin <noreply@garmin.com>':
            logging.debug('Not a garmin email: %s (Wrong From)', m)
            return
        subject = SUBJECT_REGEX.match(headers.get('Subject', ''))
        name = subject.groupdict().get('name', None) if subject else None
        if name is None:
            logging.debug('Not a garmin email: %s (Wrong Subject)', m)
            return

        body = base64.urlsafe_b64decode(
            response['payload']['body']['data'].encode('ASCII')
        ).decode('utf-8')
        soup = BeautifulSoup(body, features='html.parser')
        livetrack_urls = [
            link['href']
            for link in soup.findAll('a', href=re.compile('livetrack.garmin.com'))
        ]
        if not livetrack_urls:
            logging.debug('Invalid Garmin email: %s (Unparsable)', m)
            return
        if len(livetrack_urls) != 1:
            logging.debug(
                'Invalid Garmin email: %s (Too many livetrack URLs: %s)',
                m,
                len(livetrack_urls),
            )
            return

        return livetrack_urls[0]

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

from google.cloud.datastore.entity import Entity

from shared import auth_util
from shared import ds_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.bot import Bot
from shared.datastore.service import Service
from shared.datastore.user import User
from shared.exceptions import SyncException
from shared.services.google.client import create_gmail_client

import sync_helper


module = flask.Blueprint('google', __name__)

SUBJECT_REGEX = re.compile(r"Watch (?P<name>.*)'s live activity now!")


@module.route('/tasks/sync', methods=['POST'])
def sync():
    logging.debug('Syncing: google')
    payload = task_util.get_payload(flask.request)

    service = ds_util.client.get(payload['service_key'])
    if not Service.has_credentials(service):
        Service.set_sync_finished(service, error='No credentials')
        return responses.OK_NO_CREDENTIALS

    try:
        Service.set_sync_started(service)
        client = create_gmail_client(service)
        sync_helper.do(Worker(service, client), work_key=service.key)
        Service.set_sync_finished(service)
        return responses.OK
    except SyncException as e:
        Service.set_sync_finished(service, error=str(e))
        return responses.OK_SYNC_EXCEPTION


@module.route('/pubsub/rides', methods=['POST'])
def pubsub_rides():
    if flask.request.args.get('token', '') != config.pubsub_creds['token']:
        return responses.INVALID_TOKEN

    envelope = json.loads(flask.request.data)
    data = json.loads(base64.b64decode(envelope['message']['data']))
    logging.debug('pubsub_rides: Received data: %s', data)

    uid = auth_util.get_uid_by_email(data['emailAddress'])
    user = User.from_uid(uid)

    task_util.google_tasks_rides(user, data)

    return responses.OK


@module.route('/tasks/rides', methods=['POST'])
def tasks_rides():
    payload = task_util.get_payload(flask.request)

    service = Service.get('google', Bot.key())
    data = payload['data']
    logging.info('tasks_rides: %s', data.get('historyId'))

    try:
        client = create_gmail_client(service)
        sync_helper.do(
            PubsubWorker(service, data, client),
            work_key='%s/%s' % (service.key.parent.name, data['historyId']),
        )
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


class Worker(object):
    def __init__(self, service, client):
        self.service = service
        self.client = client

    def sync(self):
        request = {
            'labelIds': ['INBOX'],
            'topicName': 'projects/%s/topics/rides' % (config.project_id,),
        }
        watch = self.client.users().watch(userId='me', body=request).execute()
        self.service['settings']['watch'] = watch
        logging.debug('Watching: %s -> %s', self.service.key, watch)

        # Maybe Trigger a sync starting from the existing historyId
        synced_history_id = self.service['settings'].get('synced_history_id', 0)
        logging.debug(
            'synced_history_id: %s, watch history id: %s',
            synced_history_id,
            watch['historyId'],
        )

        if synced_history_id == 0:
            try:
                return self.full_sync()
            finally:
                ds_util.client.put(self.service)
        elif synced_history_id < int(watch['historyId']):
            # This shouldn't ever happen, since we use pubsub, but if it does,
            # we need to sync the latest.
            user = ds_util.client.get(self.service.key.parent)
            task_util.google_tasks_rides(user, {'historyId': synced_history_id})
            return responses.OK
        else:
            logging.debug('Nothing to sync')
            return responses.OK

    def full_sync(self):
        def process_message(request_id, response, exception):
            message_history_id = int(response['historyId'])
            synced_history_id = self.service['settings'].get('synced_history_id', 0)
            if message_history_id > synced_history_id:
                self.service['settings']['synced_history_id'] = message_history_id

            garmin_url = _extract_garmin_url(request_id, response)
            if garmin_url is not None:
                task_util.garmin_tasks_livetrack(garmin_url)

        logging.debug('Fetching the latest 100 messages')
        request = (
            self.client.users()
            .messages()
            .list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=100,
            )
        )
        batch = self.client.new_batch_http_request(callback=process_message)
        batch_size = 0
        while request is not None and batch_size < 100:
            response = request.execute()
            for message in response['messages']:
                if batch_size >= 100:
                    break
                batch.add(
                    self.client.users()
                    .messages()
                    .get(userId='me', id=message['id'], format='full'),
                    request_id=message['id'],
                )
                batch_size += 1
            request = self.client.users().messages().list_next(request, response)
        batch.execute()
        return responses.OK


class PubsubWorker(object):
    def __init__(self, service: Entity, data: dict, client):
        self.service = service
        self.data = data
        self.client = client

    def sync(self):
        logging.info('PubsubWorker: sync')

        def process_message(request_id, response, exception):
            message_history_id = int(response['historyId'])
            synced_history_id = self.service['settings'].get('synced_history_id', 0)
            if message_history_id > synced_history_id:
                self.service['settings']['synced_history_id'] = message_history_id

            garmin_url = _extract_garmin_url(request_id, response)
            if garmin_url is not None:
                task_util.garmin_tasks_livetrack(garmin_url)

        request = (
            self.client.users()
            .history()
            .list(
                userId='me',
                labelId='INBOX',
                startHistoryId=self.service['settings'].get('synced_history_id'),
            )
        )
        batch = self.client.new_batch_http_request(callback=process_message)
        while request is not None:
            response = request.execute()
            for history in response.get('history', []):
                for message in history.get('messages', []):
                    batch.add(
                        self.client.users()
                        .messages()
                        .get(userId='me', id=message['id'], format='full'),
                        request_id=message['id'],
                    )
            request = self.client.users().history().list_next(request, response)
        batch.execute()

        ds_util.client.put(self.service)
        return responses.OK


def _extract_garmin_url(request_id, response):
    logging.debug('Extracting Garmin URL: %s', request_id)
    headers = dict(
        [
            (header['name'], header['value'])
            for header in response['payload']['headers']
            if header['name'] in ('From', 'To', 'Subject')
        ]
    )
    logging.debug('Fetched message: %s', request_id)
    if headers.get('From') != 'Garmin <noreply@garmin.com>':
        logging.debug('Not a garmin email: %s (Wrong From)', request_id)
        return
    subject = SUBJECT_REGEX.match(headers.get('Subject', ''))
    name = subject.groupdict().get('name', None) if subject else None
    if name is None:
        logging.debug('Not a garmin email: %s (Wrong Subject)', request_id)
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
        logging.debug('Invalid Garmin email: %s (Unparsable)', request_id)
        return
    if len(livetrack_urls) != 1:
        logging.debug(
            'Invalid Garmin email: %s (Too many livetrack URLs: %s)',
            request_id,
            len(livetrack_urls),
        )
        return

    return livetrack_urls[0]

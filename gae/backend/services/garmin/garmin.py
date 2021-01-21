# Copyright 2020 Google LLC
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

import datetime
import logging
import re

import flask
import requests

import dateutil.parser

from shared import auth_util
from shared import ds_util
from shared import responses
from shared import task_util
from shared.services.garmin import client as garmin_client
from shared.exceptions import SyncException
from shared.datastore.series import Series

import sync_helper


module = flask.Blueprint('garmin', __name__)

LIVETRACK_INFO_URL = 'https://livetrack.garmin.com/services/session/%(session)s/sessionToken/%(token)s?requestTime=%(requestTime)s'
LIVETRACK_TRACKPOINTS_FIRST_URL = 'https://livetrack.garmin.com/services/session/%(session)s/trackpoints?requestTime=%(requestTime)s'
LIVETRACK_TRACKPOINTS_URL = 'https://livetrack.garmin.com/services/session/%(session)s/trackpoints?requestTime=%(requestTime)s&from=%(from)s'


@module.route('/process/livetrack', methods=['POST'])
def process_livetrack():
    auth_util.verify(flask.request)
    params = task_util.get_payload(flask.request)
    url = params['url']
    logging.info('process/livetrack: %s', url)

    try:
        sync_helper.do(LivetrackWorker(url=url), work_key=url)
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


class Worker(object):
    def __init__(self, service):
        self.service = service
        self.client = garmin_client.create(service)

    def sync(self):
        self.sync_user()
        self.sync_measures()

    def sync_user(self):
        logging.debug('sync_user: %s', self.client.profile)

    def sync_measures(self):
        end_date = datetime.datetime.now(tz=datetime.timezone.utc).date()
        start_date = end_date - datetime.timedelta(days=365)

        # stats = self.client.get_stats(end_date.isoformat())
        body_comp = self.client.get_body_comp(
            start_date.isoformat(), end_date.isoformat()
        )

        series = Series.to_entity(body_comp['dateWeightList'], parent=self.service.key)

        ds_util.client.put(series)


class LivetrackWorker(object):
    def __init__(self, url):
        self.url = url

    def sync(self):
        match = re.match(r'.*/session/(?P<session>.*)/token/(?P<token>.*)', self.url)
        url_info = match.groupdict() if match else dict()
        if 'session' not in url_info or 'token' not in url_info:
            logging.debug(
                'Invalid Garmin email: %s (Unable to get url_info: %s)',
                self.url,
                str(url_info.keys()),
            )
            return responses.OK_INVALID_LIVETRACK
        self._process_livetrack(url_info)
        return responses.OK

    def _process_livetrack(self, url_info):
        """Now we know enough to fetch livetrack info."""
        session = requests.Session()
        now = datetime.datetime.now(datetime.timezone.utc)
        now_millis = int(now.timestamp() * 1000)

        # Gets info about the session, such as a user's name.
        response = session.get(
            LIVETRACK_INFO_URL % dict(**url_info, **{'requestTime': now_millis})
        )
        if response.status_code != 200:
            logging.debug('Invalid LiveTrack: %s (No session info)', self.url)
            return
        livetrack_info = response.json()

        # livetrack_start = livetrack_info['session']['start']
        # livetrack_start_millis = int(
        #     dateutil.parser.parse(livetrack_info['session']['start']).timestamp() * 1000
        # )
        ended_ago = now - dateutil.parser.parse(livetrack_info['session']['end'])
        if ended_ago:
            logging.debug(
                'Invalid LiveTrack: %s (Already finished %s ago)', self.url, ended_ago
            )

        # Gets some coures info, like perhaps, where they currently are.
        response = session.get(
            LIVETRACK_TRACKPOINTS_FIRST_URL
            % dict(**livetrack_info, **{'requestTime': now_millis})
        )
        if response.status_code != 200:
            logging.debug('Invalid LiveTrack: %s (Failed fetching points)', self.url)
            return
        track_points = response.json().get('trackPoints', [])
        if not track_points:
            logging.debug('Invalid LiveTrack: %s (0 points)', self.url)
            return
        logging.debug(
            'Found livetrack points: %s: %s %s',
            self.url,
            response.url,
            len(track_points),
        )
        recent_millis = (
            dateutil.parser.parse(track_points[-1]['dateTime']).timestamp() * 1000
        )
        # I can use recent_millis to get only the latest points from livetracks, if i wanted.
        logging.debug(
            'Found most recent livetrack points: %s: %s %s',
            self.url,
            response.url,
            recent_millis,
        )

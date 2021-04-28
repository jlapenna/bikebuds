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
import json
import logging
import re

from google.cloud.datastore.entity import Entity
import dateutil.parser
import flask
import requests

from shared import ds_util
from shared import responses
from shared import task_util
from shared.datastore.series import Series
from shared.datastore.service import Service
from shared.datastore.track import Track
from shared.exceptions import SyncException
from shared.services.garmin import client as garmin_client

import sync_helper


module = flask.Blueprint('garmin', __name__)


LIVETRACK_INFO_URL = 'https://livetrack.garmin.com/services/session/%(session)s/sessionToken/%(token)s?requestTime=%(requestTime)s'
LIVETRACK_TRACKPOINTS_FIRST_URL = 'https://livetrack.garmin.com/services/session/%(session)s/trackpoints?requestTime=%(requestTime)s'
LIVETRACK_TRACKPOINTS_URL = 'https://livetrack.garmin.com/services/session/%(session)s/trackpoints?requestTime=%(requestTime)s&from=%(from)s'


@module.route('/process/livetrack', methods=['POST'])
def process_livetrack():
    params = task_util.get_payload(flask.request)
    url = params['url']
    logging.info('process/livetrack: %s', url)

    try:
        sync_helper.do(TrackWorker(url=url), work_key=url)
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


@module.route('/tasks/sync', methods=['POST'])
def sync():
    logging.debug('Syncing: garmin')
    params = task_util.get_payload(flask.request)

    service = ds_util.client.get(params['service_key'])
    if not Service.has_credentials(service, required_key='password'):
        logging.warning('No creds: %s', service.key)
        Service.set_sync_finished(service, error='No credentials')
        return responses.OK_NO_CREDENTIALS

    try:
        Service.set_sync_started(service)
        sync_helper.do(Worker(service), work_key=service.key)
        Service.set_sync_finished(service)
        return responses.OK
    except SyncException as e:
        Service.set_sync_finished(service, error=str(e))
        return responses.OK_SYNC_EXCEPTION


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


class TrackWorker(object):
    def __init__(self, url: str):
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

        track_entity = _process_livetrack(self.url, url_info)
        ds_util.client.put(track_entity)
        if track_entity.get('status', Track.STATUS_UNKNOWN) <= 0:
            logging.warning('Sync failed: %s', track_entity)
            return responses.OK_INVALID_LIVETRACK
        return responses.OK


def _process_livetrack(url: str, url_info: dict) -> Entity:
    """Now we know enough to fetch livetrack info."""
    track = {'url': url, 'url_info': url_info}

    session = requests.Session()

    # Gets info about the session, such as a user's name.
    now = datetime.datetime.now(datetime.timezone.utc)
    request_time_millis = int(now.timestamp() * 1000)
    response = session.get(
        LIVETRACK_INFO_URL % dict(**url_info, **{'requestTime': request_time_millis})
    )
    if response.status_code != 200:
        logging.warning(
            'Invalid Track: http failed fetching session: %s',
            response.status_code,
        )
        track['status'] = Track.STATUS_FAILED
        return Track.to_entity(track)

    response_json = response.json()
    logging.debug('info_url response: %s', json.dumps(response_json))
    if response_json.get('statusCode', 200) != 200:
        logging.debug('Invalid Track: %s (No session info)', url)
        track['status'] = Track.STATUS_FAILED
        return Track.to_entity(track)
    track['info'] = response_json
    track['status'] = Track.STATUS_INFO

    if 'start' in track['info']['session']:
        track['status'] = Track.STATUS_STARTED
        # livetrack_start_millis = int(
        #     dateutil.parser.parse(track['session_data']['session']['start']).timestamp()
        #     * 1000
        # )
    if 'end' in track['info']['session']:
        ended_ago = now - dateutil.parser.parse(track['info']['session']['end'])
        if ended_ago:
            logging.debug(
                'Expired LiveTrack: %s (Already finished %s ago)', url, ended_ago
            )
        track['status'] = Track.STATUS_FINISHED
        return Track.to_entity(track)

    # Gets some coures info, like perhaps, where they currently are.
    response = session.get(
        LIVETRACK_TRACKPOINTS_FIRST_URL
        % dict(**track['url_info'], **{'requestTime': request_time_millis})
    )
    if response.status_code != 200:
        logging.debug('Invalid LiveTrack: %s http failed fetching points', url)
        track['status'] = Track.STATUS_FAILED
        return Track.to_entity(track)

    response_json = response.json
    logging.debug('Ended Track: %s', json.dumps(response_json))
    logging.debug('Trackpoints Response json: %s', json.dumps(response_json))
    track['trackpoints'] = response_json
    track['status'] = Track.STATUS_TRACKPOINTS

    if not 'trackPoints' not in track:
        logging.debug('Invalid LiveTrack: %s (0 points)', url)
    logging.debug(
        'Found livetrack points: %s -> %s',
        url,
        len(track['trackPoints']),
    )
    most_recent_millis = (
        dateutil.parser.parse(track['trackPoints'][-1]['dateTime']).timestamp() * 1000
    )
    # I can use most_recent_millis to get only the latest points from livetracks, if i wanted.
    logging.debug(
        'Found most recent livetrack points: %s: %s %s',
        url,
        response.url,
        most_recent_millis,
    )
    track['status'] = Track.SUCCESS
    return Track.to_entity(track)

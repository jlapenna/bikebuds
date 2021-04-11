# Copyright 2018 Google LLC
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

import logging

import flask

from shared import ds_util
from shared import googlemaps_util
from shared import responses
from shared import task_util
from shared.datastore.activity import Activity
from shared.datastore.athlete import Athlete
from shared.datastore.bot import Bot
from shared.datastore.route import Route
from shared.datastore.segment import Segment
from shared.datastore.segment_effort import SegmentEffort
from shared.datastore.service import Service
from shared.exceptions import SyncException
from shared.services.strava.client import ClientWrapper
from shared.services.strava.club_worker import ClubWorker

from services.strava.events_worker import EventsWorker

import sync_helper


module = flask.Blueprint('strava', __name__)


@module.route('/tasks/sync', methods=['POST'])
def sync():
    logging.debug('Syncing: strava')
    params = task_util.get_payload(flask.request)

    service = ds_util.client.get(params['service_key'])
    if not Service.has_credentials(service):
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


@module.route('/tasks/sync/club/<club_id>', methods=['GET', 'POST'])
def sync_club(club_id):
    logging.debug('Syncing: %s', club_id)
    service = Service.get('strava', parent=Bot.key())
    sync_helper.do(ClubWorker(club_id, service), work_key=service.key)
    return responses.OK


@module.route('/tasks/process_event', methods=['POST'])
def process_event_task():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('Event: %s', event.key)

    # First try to get the service using the event.key's service.
    # If this event is coming from an old subscription / secret url, which
    # embeds a service_key in it, then we might get these.
    service_key = event.key.parent
    service = ds_util.client.get(service_key)

    if service is None:
        logging.error('Event: No service: %s', event.key)
        return responses.OK_NO_SERVICE

    if not Service.has_credentials(service):
        logging.warning('Event: No credentials: %s', event.key)
        return responses.OK_NO_CREDENTIALS

    try:
        sync_helper.do(EventsWorker(service, event), work_key=event.key)
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


class Worker(object):
    def __init__(self, service):
        self.service = service
        self.client = ClientWrapper(service)

    def sync(self):
        self.sync_athlete()
        self.sync_activities()
        self.sync_routes()
        self.sync_segments()

    def sync_athlete(self):
        self.client.ensure_access()

        athlete = self.client.get_athlete()
        ds_util.client.put(Athlete.to_entity(athlete, parent=self.service.key))

    def sync_activities(self):
        self.client.ensure_access()

        athlete = self.client.get_athlete()

        for activity in self.client.get_activities():
            # Track full activity info (detailed), not returned by the normal
            # get_activities (summary) request.
            detailed_activity = self.client.get_activity(activity.id)
            activity_entity = Activity.to_entity(
                detailed_activity, detailed_athlete=athlete, parent=self.service.key
            )
            ds_util.client.put(activity_entity)

            # But also add all the user's best efforts.
            for segment_effort in detailed_activity.segment_efforts:
                segment_effort_entity = SegmentEffort.to_entity(
                    segment_effort, parent=self.service.key
                )
                ds_util.client.put(segment_effort_entity)

    def sync_routes(self):
        self.client.ensure_access()

        for route in self.client.get_routes():
            ds_util.client.put(Route.to_entity(route, parent=self.service.key))

    def sync_segments(self):
        self.client.ensure_access()

        for segment in self.client.get_starred_segments():
            # Track full segment info (detailed), not returned by the normal
            # get_starred_segments (summary) request.
            detailed_segment = self.client.get_segment(segment.id)
            elevations = self._fetch_segment_elevation(detailed_segment)
            segment_entity = Segment.to_entity(
                detailed_segment, elevations=elevations, parent=self.service.key
            )
            ds_util.client.put(segment_entity)

    def _fetch_segment_elevation(self, segment):
        return [
            {
                'location': {
                    'latitude': e['location']['lat'],
                    'longitude': e['location']['lng'],
                },
                'elevation': e['elevation'],
                'resolution': e['resolution'],
            }
            for e in googlemaps_util.client.elevation_along_path(
                segment.map.polyline, samples=100
            )
        ]

    def _sync_activity(self, activity_id):
        """Gets additional info: description, calories and embed_token."""
        activity = self.client.get_activity(activity_id)
        return ds_util.client.put(Activity.to_entity(activity, parent=self.service.key))

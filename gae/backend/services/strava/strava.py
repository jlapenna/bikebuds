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

from shared import ds_util
from shared import googlemaps_util
from shared.datastore.activity import Activity
from shared.datastore.athlete import Athlete
from shared.datastore.route import Route
from shared.datastore.segment import Segment

from shared.services.strava.client import ClientWrapper


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

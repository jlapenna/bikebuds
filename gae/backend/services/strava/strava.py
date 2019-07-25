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
from shared.datastore.activity import Activity
from shared.datastore.athlete import Athlete

from services.strava.client import ClientWrapper


class Worker(object):
    def __init__(self, service):
        self.service = service
        self.client = ClientWrapper(service)

    def sync(self):
        self.sync_athlete()
        self.sync_activities()

    def sync_athlete(self):
        self.client.ensure_access()

        athlete = self.client.get_athlete()
        ds_util.client.put(Athlete.to_entity(athlete, parent=self.service.key))

    def sync_activities(self):
        self.client.ensure_access()

        athlete = self.client.get_athlete()
        athlete_clubs = [club.id for club in athlete.clubs]

        # Track the clubs that these activities were a part of, by annotating
        # them with the athlete's clubs.
        for activity in self.client.get_activities():
            activity_entity = Activity.to_entity(activity, parent=self.service.key)
            activity_entity['clubs'] = athlete_clubs
            ds_util.client.put(activity_entity)

    def _sync_activity(self, activity_id):
        """Gets additional info: description, calories and embed_token."""
        activity = self.client.get_activity(activity_id)
        return ds_util.client.put(Activity.to_entity(activity, parent=self.service.key))

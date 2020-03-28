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
from shared.datastore.athlete import Athlete
from shared.datastore.activity import Activity
from shared.datastore.club import Club

from shared.services.strava.client import ClientWrapper


class ClubWorker(object):
    def __init__(self, club_id, service):
        self.club_id = club_id
        self.service = service
        self.client = ClientWrapper(service)

    def sync(self):
        self.sync_club()
        club = self.sync_activities()
        return club

    def sync_club(self):
        self.client.ensure_access()

        club = self.client.get_club(self.club_id)
        club_entity = Club.to_entity(club, parent=self.service.key)
        club_entity['members'] = [Athlete.to_entity(member) for member in club.members]
        ds_util.client.put(club_entity)
        return club_entity

    def sync_activities(self):
        self.client.ensure_access()

        with ds_util.client.transaction():
            club = Club.get(self.club_id, parent=self.service.key)
            activity_query = ds_util.client.activity_query(
                kind='Activity', ancestor=club.key
            )
            activity_query.keys_only()
            ds_util.client.delete_multi(
                activity.key for activity in activity_query.fetch()
            )
            for activity in self.client.get_club_activities(club.id):
                activity_entity = Activity.to_entity(activity, parent=club.key)
                ds_util.client.put(activity_entity)
        return club

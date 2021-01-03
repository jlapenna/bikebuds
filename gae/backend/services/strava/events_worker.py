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

from shared import ds_util
from shared.datastore.activity import Activity
from shared.datastore.athlete import Athlete

from shared.services.strava.client import ClientWrapper


class EventsWorker(object):
    def __init__(self, service, event):
        self.service = service
        self.event = event
        self.client = ClientWrapper(service)

    def sync(self):
        self.client.ensure_access()

        object_id = self.event.get('object_id')
        object_type = self.event.get('object_type')
        aspect_type = self.event.get('aspect_type')
        with ds_util.client.transaction():
            logging.debug(
                'StravaEvent: process_event_batch:  %s, %s',
                object_id,
                self.event.key,
            )

            if object_type == 'activity':
                if aspect_type == 'delete':
                    activity_key = ds_util.client.key(
                        'Activity', object_id, parent=self.service.key
                    )
                    ds_util.client.delete(activity_key)
                    logging.info(
                        'StravaEvent: Deleted Activity: %s: %s',
                        activity_key,
                        self.event.key,
                    )
                else:
                    athlete = self.client.get_athlete()
                    activity = self.client.get_activity(object_id)
                    activity_entity = Activity.to_entity(
                        activity, detailed_athlete=athlete, parent=self.service.key
                    )
                    ds_util.client.put(activity_entity)
                    logging.info(
                        'StravaEvent: Created: %s: %s',
                        activity_entity.key,
                        self.event.key,
                    )
            elif object_type == 'athlete':
                athlete = self.client.get_athlete()
                athlete_entity = Athlete.to_entity(athlete, parent=self.service.key)
                ds_util.client.put(athlete_entity)
                logging.info(
                    'StravaEvent: Updated Athlete: %s: %s',
                    athlete_entity.key,
                    self.event.key,
                )
                activities_query = ds_util.client.query(
                    kind='Activity', ancestor=self.service.key
                )
                for activity in activities_query.fetch():
                    activity['athlete'] = athlete
                    ds_util.client.put(activity)
                logging.info(
                    'StravaEvent: Updated Activities: %s: %s',
                    athlete_entity.key,
                    self.event.key,
                )
            else:
                logging.warn(
                    'StravaEvent: Update object_type %s not implemented: %s',
                    object_type,
                    self.event.key,
                )

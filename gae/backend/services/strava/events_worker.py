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

import collections
import logging

from shared import ds_util
from shared.datastore.activity import Activity
from shared.datastore.athlete import Athlete

from shared.services.strava.client import ClientWrapper


class EventsWorker(object):
    def __init__(self, service):
        self.service = service
        self.client = ClientWrapper(service)

    def sync(self):
        self.client.ensure_access()

        query = ds_util.client.query(
            kind='SubscriptionEvent', ancestor=self.service.key
        )
        events = query.fetch()
        events = sorted(events, key=lambda x: x['event_time'])
        batches = collections.defaultdict(list)
        for event in events:
            batches[(event['object_id'], event['object_type'])].append(event)

        athlete = self.client.get_athlete()
        for (object_id, object_type), batch in batches.items():
            self._process_event_batch(athlete, object_id, object_type, batch)

    def _process_event_batch(self, athlete, object_id, object_type, batch):
        with ds_util.client.transaction():
            logging.debug(
                'process_event_batch:  %s, %s, %s',
                self.service.key,
                object_id,
                len(batch),
            )

            # We're no longer going to need these.
            ds_util.client.delete_multi((event.key for event in batch))

            if object_type == 'activity':
                operations = [event['aspect_type'] for event in batch]

                if 'delete' in operations:
                    activity_key = ds_util.client.key(
                        'Activity', object_id, parent=self.service.key
                    )
                    ds_util.client.delete(activity_key)
                    logging.info('Deleted: Entity: %s', activity_key)
                else:
                    activity = self.client.get_activity(object_id)
                    activity_entity = Activity.to_entity(
                        activity, detailed_athlete=athlete, parent=self.service.key
                    )
                    ds_util.client.put(activity_entity)
                    logging.info('Created: %s -> %s', activity.id, activity_entity.key)
            elif object_type == 'athlete':
                ds_util.client.put(Athlete.to_entity(athlete, parent=self.service.key))
                activities_query = ds_util.client.query(
                    kind='Activity', ancestor=self.service.key
                )
                for activity in activities_query.fetch():
                    activity['athlete'] = athlete
                    ds_util.client.put(activity)
            else:
                logging.warn('Update object_type not implemented: %s', object_type)

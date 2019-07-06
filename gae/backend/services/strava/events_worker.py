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

from services.strava.client import ClientWrapper


class EventsWorker(object):
    def __init__(self, service):
        self.service = service
        self.client = ClientWrapper(service)

    def sync(self):
        self.client.ensure_access()

        query = ds_util.client.query(
            kind='SubscriptionEvent', ancestor=self.service.key, order=['-event_time']
        )
        events = query.fetch()
        batches = collections.defaultdict(list)
        for event in events:
            batches[(event['object_id'], event['object_type'])].append(event)
        for ((object_id, object_type), batch) in batches.items():
            self._process_event_batch(
                self.client, self.service, object_id, object_type, batch
            )

    def _process_event_batch(client, service, object_id, object_type, batch):
        with ds_util.client.transaction():
            logging.debug(
                'process_event_batch:  %s, %s, %s', service.key, object_id, len(batch)
            )

            if object_type != 'activity':
                logging.warn('Update object_type not implemented: %s', object_type)
                return

            operations = [event['aspect_type'] for event in batch]

            if 'delete' in operations:
                activity_key = ds_util.client.key(
                    'Activity', object_id, parent=service.key
                )
                activity_key.delete()
                logging.info('Deleted: Entity: %s', activity_key)
            else:
                activity = client.get_activity(object_id)
                activity_entity = Activity.to_entity(activity, parent=service.key)
                # get_activity returns a MetaAthelte, which only has an
                # athlete_id, replace from the stored athlete entity.
                athlete_entity = Athlete.get_private(service.key)
                activity_entity['athlete'] = athlete_entity
                ds_util.client.put(activity_entity)
                activity_key = activity_entity.key
                logging.info('Created: %s -> %s', activity.id, activity_key)

            ds_util.client.delete_multi((event.key for event in batch))

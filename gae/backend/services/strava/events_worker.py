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
import datetime
import functools
import logging
import random
import time

from shared import ds_util
from shared.config import config
from shared.datastore.activity import Activity
from shared.datastore.athlete import Athlete
from shared.datastore.club import Club
from shared.datastore.service import Service

import stravalib
from stravalib import exc

from services.strava.client import ClientWrapper


class EventsWorker(object):
    def __init__(self, service):
        self.service = service
        self.client = ClientWrapper(service)

    def sync(self):
        self.client.ensure_access()

        query = ds_util.client.query(kind='SubscriptionEvent',
                ancestor=self.service.key, order=['-event_time'])
        events = query.fetch()
        batches = collections.defaultdict(list)
        for event in events:
            batches[(event['object_id'], event['object_type'])].append(event)
        for (object_id, object_type), batch in batches.items():
            self._process_event_batch(
                    self.client, self.service, object_id, object_type, batch)


    def _process_event_batch(client, service, object_id, object_type, batch):
        with ds_util.client.transaction():
            logging.debug('process_event_batch:  %s, %s, %s',
                    service.key, object_id, len(batch))

            if object_type != 'activity':
                logging.warn('Update object_type not implemented: %s', object_type)
                return

            operations = [event['aspect_type'] for event in batch]

            if 'delete' in operations:
                activity_key = ds_util.client.key('Activity', object_id, parent=service.key)
                result = activity_key.delete()
                logging.info('Deleted: Entity: %s', activity_key)
            else:
                activity = client.get_activity(object_id)
                activity_entity = Activity.to_entity(activity, parent=service.key)
                # get_activity returns a MetaAthelte, which only has an athlete id,
                # replace from the stored athlete entity.
                athlete_entity = Athlete.get_private(service.key)
                activity_entity['athlete'] = athlete_entity
                ds_util.client.put(activity_entity)
                activity_key = activity_entity.key
                logging.info('Created: %s -> %s', activity.id, activity_key)

            ds_util.client.delete_multi((event.key for event in batch))


class ClientWrapper(object):
    """Auto-refresh (once) access tokens on any request."""
    def __init__(self, service):
        self._service = service
        self._client = stravalib.client.Client(
                access_token=service['credentials']['access_token'],
                rate_limiter=(lambda x=None: None))

    def ensure_access(self):
        """Ensure that an access token is good for at least 60 more seconds."""
        now = time.time()
        expires_around = self._service['credentials']['expires_at'] - 60
        if time.time() > expires_around:
            seconds_ago = now - expires_around
            logging.info('Access expired %s ago; fetching new', seconds_ago)
            self._refresh_credentials()

    def __getattr__(self, attr):
        func = getattr(self._client, attr)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exc.AccessUnauthorized as e: 
                logging.info("Token expired, refreshing.", e)
                self._refresh_credentials()
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper

    def _refresh_credentials(self):
        new_credentials = self._client.refresh_access_token(
            client_id=config.strava_creds['client_id'],
            client_secret=config.strava_creds['client_secret'],
            refresh_token=self._service['credentials']['refresh_token'])
        Service.update_credentials(self._service, dict(new_credentials))
        self._client.access_token = self._service['credentials']['access_token']


def _add_test_sub_events():
    service_key = Athlete.get_by_id(35056021, keys_only=True).parent
    e = Entity(ds_util.client.key('SubscriptionEvent', parent=service_key))
    e.update(
            {'aspect_type': 'create',
                'event_time': 1549151210,
                'object_id': 2120517766,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {}
                })
    ds_util.client.put(e)
    e = Entity(ds_util.client.key('SubscriptionEvent', parent=service_key))
    e.update(
            {'aspect_type': 'update',
                'event_time': 1549151212,
                'object_id': 2120517766,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {'title': 'Updated Title'}
                })
    ds_util.client.put(e)
    e = Entity(ds_util.client.key('SubscriptionEvent', parent=service_key))
    e.update(
            {'aspect_type': 'create',
                'event_time': 1549151211,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {}
                })
    ds_util.client.put(e)
    e = Entity(ds_util.client.key('SubscriptionEvent', parent=service_key))
    e.update(
            {'aspect_type': 'update',
                'event_time': 1549151213,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {'title': 'Second Updated Title'}
                })
    ds_util.client.put(e)
    e = Entity(ds_util.client.key('SubscriptionEvent', parent=service_key))
    e.update(
            {'aspect_type': 'delete',
                'event_time': 1549151214,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {}
                })
    ds_util.client.put(e)

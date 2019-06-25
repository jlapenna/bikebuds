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

import stravalib
from stravalib import exc

from shared import ds_util
from shared.config import config
from shared.datastore.activity import Activity
from shared.datastore.athlete import Athlete
from shared.datastore.club import Club
from shared.datastore.service import Service

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
            activity_entity = Activity.to_entity(
                    activity, parent=self.service.key)
            activity_entity['clubs'] = athlete_clubs
            ds_util.client.put(activity_entity)

    def _sync_activity(self, activity_id):
        """Gets additional info: description, calories and embed_token."""
        activity = self.client.get_activity(activity_id)
        return ds_util.client.put(
                Activity.to_entity(activity, parent=self.service.key))


class ClubWorker(object):

    def __init__(self, club_id):
        self.club_id = club_id
        self.service = None
        self.client = None

    def _init_client(self):
        query = ds_util.client.query(kind='Athlete')
        query.add_filter('clubs.id', '=', int(self.club_id))
        query.add_filter('clubs.admin', '=', True)
        query.keys_only()
        admin_service_keys = [athlete.key.parent for athlete in query.fetch()]
        if len(admin_service_keys) == 0:
            logging.warn(
                    'ClubWorker: Cannot sync %s without an admin',
                    self.club_id)
            return False

        # TODO: We might some day want to randomly select an admin by which to
        # fetch club details, rather than the first.
        self.service = ds_util.client.get(admin_service_keys[0])
        if self.service is None:
            logging.error(
                    'ClubWorker: Cannot sync %s without a service',
                    self.club_id)
            return False

        logging.debug(
                'ClubWorker: Using %s for %s', self.service.key, self.club_id)
        self.client = ClientWrapper(self.service)
        return True

    def sync(self):
        if not self._init_client():
            logging.error(
                    'ClubWorker: Cannot sync %s, no client.', self.club_id)
            return

        # Create a club id'ed by the club_id but without a parent.
        # Note, per the docs, a parentless entity won't be returned by a query
        # with ancestor=None
        # TODO: We shouldn't put member-specific  fields in this entity.
        club_result = self.client.get_club(self.club_id)
        club_entity = ds_util.put(Club.to_entity(club_result))

        # These athlete responses don't have ids, so we can't really use this
        # result. [<Athlete id=None firstname='Matt' lastname='C.'>, ...]
        #members_result = [m for m in self.client.get_club_members(self.club_id)]
        #logging.debug(members_result)

        # By way of fetching athletes, we've also found their memberships.
        # Fetch those athletes.
        query = ds_util.client.query(kind='Athlete')
        query.add_filter('clubs.id', '=', int(self.club_id))
        query.keys_only()
        athlete_keys = [athlete.key for athlete in query.fetch()]


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

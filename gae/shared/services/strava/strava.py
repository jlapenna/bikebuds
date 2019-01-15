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

from google.appengine.ext import deferred
from google.appengine.ext import ndb

from shared.config import config
from shared.datastore import services
from shared.datastore.activities import Activity
from shared.datastore.athletes import Athlete, ClubRef
from shared.datastore.clubs import Club, AthleteRef
from shared.datastore.services import Service

import stravalib
from stravalib import exc


class AthleteSynchronizer(object):

    def sync(self, service):
        client = ClientWrapper(service)
        client.ensure_access()
        athlete = client.get_athlete()
        return Athlete.entity_from_strava(service.key, athlete).put()


class ActivitiesSynchronizer(object):

    def sync(self, service):
        client = ClientWrapper(service)
        client.ensure_access()

        activities = []
        for activity in client.get_activities():
            if activity.type != 'Ride':
                continue
            activities.append(activity)

        @ndb.transactional
        def put():
            ndb.put_multi(Activity.from_strava(service.key, activity)
                    for activity in activities)
        return put()

    def _sync_activity(self, service, activity_id):
        """Gets additional info: description, calories and embed_token."""
        client = ClientWrapper(service)
        client.ensure_access()
        activity = client.get_activity(activity_id)
        return Activity.from_strava(service.key, activity).put()


class ClubsSynchronizer(object):
    """Syncs all clubs an athlete is an admin or member of."""

    def sync(self, service):
        client = ClientWrapper(service)
        client.ensure_access()

        athlete_entity = Athlete.get_private(service.key)
        for club_ref in athlete_entity.athlete.clubs:
            logging.info('Fetching club: %s', club_ref.id)
            club_result = client.get_club(club_ref.id)
            club_entity = Club.entity_from_strava(club_result)

            if (not club_result.private
                    or club_result.admin
                    or club_result.owner
                    or club_result.membership == 'member'):
                logging.info('Putting club: %s', club_entity.key.id())
                club_entity.put()


class ClubsMembersProcessor(object):
    """Syncs all clubs an athlete is an admin or member of."""

    def sync(self):
        clubs_to_put = []
        for club_entity in Club.query():
            logging.info('Joining club: %s', club_entity.key.id())
            athletes_query = Athlete.query(
                        Athlete.athlete.clubs.id == club_entity.key.id())
            club_entity.club.members = [
                    AthleteRef.from_strava(athlete_entity.athlete)
                    for athlete_entity in athletes_query.fetch()]
            clubs_to_put.append(club_entity)
        ndb.put_multi(clubs_to_put)


class ClubActivitiesSharedSynchronizer(object):
    """Syncs all club activities."""

    def sync(self):
        athlete_entities = Athlete.query().fetch()
        club_to_users = collections.defaultdict(lambda: set())
        for athlete_entity in athlete_entities:
            for club in athlete_entity.athlete.clubs:
                club_to_users[club.key.id()].add(athlete_entity.key.id())
        for club_id, members in club_to_users.iteritems():
            athlete_entities = (
                    Athlete.query(
                        Athlete.strava_id.IN(members))
                    .order(Athlete.strava_id)
                    .fetch(keys_only=True)
                    )
            service_keys = [athlete_entity.parent()
                    for athlete_entity in athlete_entities]
            service_entities = Service.query(Service.key.IN(service_entity_keys),
                    Service.credentials != None).fetch()
            if len(service_entities) == 0:
                logging.warn('No creds to sync club %s. Unexpected.', club_id)
            random.shuffle(service_entities)

            # Just use the first creds for now.
            service_entity = service_entities[0]
            client = ClientWrapper(service_entity)
            activities = client.get_club_activities(club_id)

            @ndb.transactional
            def put():
                ndb.put_multi(Activity.entity_from_strava(ndb.Key(Club, club_id), activity)
                        for activity in activities)
            put()


class ClientWrapper(object):
    """Auto-refresh (once) access tokens on any request."""
    def __init__(self, service):
        self._service = service
        self._client = stravalib.client.Client(
                access_token=service.get_credentials().access_token,
                rate_limiter=(lambda x=None: None))

    def ensure_access(self):
        """Ensure that an access token is good for at least another 60 seconds."""
        now = time.time()
        expires_around = self._service.get_credentials().expires_at - 60
        if time.time() > expires_around:
            seconds_ago = now - expires_around
            logging.info('Access expired %s ago; fetching a new one.',
                    seconds_ago)
            self._refresh_credentials()

    def __getattr__(self, attr):
        func = getattr(self._client, attr)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exc.AccessUnauthorized, e: 
                logging.info("Token expired, refreshing.", e)
                self._refresh_credentials()
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper

    def _refresh_credentials(self):
        new_credentials = self._client.refresh_access_token(
            client_id=config.strava_creds['client_id'],
            client_secret=config.strava_creds['client_secret'],
            refresh_token=self._service.get_credentials().refresh_token)
        self._service.update_credentials(dict(new_credentials))
        self._client.access_token = self._service.get_credentials().access_token

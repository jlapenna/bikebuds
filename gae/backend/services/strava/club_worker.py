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

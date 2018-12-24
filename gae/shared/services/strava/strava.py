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

import datetime
import functools
import logging
import time

from google.appengine.ext import deferred
from google.appengine.ext import ndb

from shared.config import config
from shared.datastore import services
from shared.datastore.activities import Activity

import stravalib
from stravalib import exc


class Synchronizer(object):
    def sync(self, service):
        client = ClientWrapper(service)
        client.ensure_access()

        activities = []
        for activity in client.get_activities():
            if activity.type != 'Ride':
                continue
            # Use this to fill in description, calories and embed_token.
            # This is not worth the cost...
            #if activity.id == '1997254642'):
            #    deferred.defer(self.sync_activity, service, activity.id)
            activities.append(activity)

        @ndb.transactional
        def put():
            ndb.put_multi(Activity.from_strava(service.key, activity)
                    for activity in activities)
        return put()

    def sync_activity(self, service, activity_id):
        client = ClientWrapper(service)
        client.ensure_access()

        activity = client.get_activity(activity_id)
        return Activity.from_strava(service.key, activity).put()


class ClientWrapper(object):
    """Auto-refresh (once) access tokens on any request."""
    def __init__(self, service):
        self._service = service
        self._client = stravalib.client.Client(
                access_token=service.get_credentials().access_token)

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

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

import functools
import logging
import time

from shared.config import config
from shared.datastore.service import Service

import stravalib
from stravalib import exc


class ClientWrapper(object):
    """Auto-refresh (once) access tokens on any request."""

    def __init__(self, service):
        self._service = service
        self._client = stravalib.client.Client(
            access_token=service['credentials']['access_token'],
            rate_limiter=(lambda x=None: None),
        )

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
            refresh_token=self._service['credentials']['refresh_token'],
        )
        Service.update_credentials(self._service, dict(new_credentials))
        self._client.access_token = self._service['credentials']['access_token']

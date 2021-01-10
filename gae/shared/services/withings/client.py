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
import logging

import arrow
import withings_api
from withings_api.common import Credentials2

from shared.config import config
from shared.datastore.service import Service

_SCOPE = (
    withings_api.AuthScope.USER_ACTIVITY,
    withings_api.AuthScope.USER_METRICS,
    withings_api.AuthScope.USER_INFO,
)


def create_client(service):
    if not Service.has_credentials(service):
        raise Exception('Cannot create Withings client without creds: %s' % (service,))
    creds_dict = service['credentials']
    creds = create_creds2(creds_dict)

    def refresh_callback(new_credentials):
        """Updates credentials.

        Params:
            new_credentials: withings_api.Credentials2
        """
        logging.debug('Withings creds refresh for: %s', service.key)
        creds_dict = create_creds_dict(new_credentials)
        Service.update_credentials(service, creds_dict)

    return withings_api.WithingsApi(creds, refresh_cb=refresh_callback)


def create_auth(callback_uri):
    return withings_api.WithingsAuth(
        client_id=config.withings_creds['client_id'],
        consumer_secret=config.withings_creds['client_secret'],
        callback_uri=callback_uri,
        scope=_SCOPE,
        mode=None,  # A bug in the library sets 'demo' by default.
    )


def create_creds_dict(creds: Credentials2):
    creds_dict = creds.dict()
    # Entities don't know arrow, they know DateTime.
    creds_dict['created'] = creds_dict['created'].datetime
    logging.debug('Created creds_dict: %s', creds_dict)
    return creds_dict


def create_creds2(creds_dict: dict):
    creds_dict = dict(creds_dict)
    now = arrow.get(datetime.datetime.utcnow())
    if 'created' not in creds_dict:
        # We have sometimes created creds that didn't store created, so we
        # really don't know when the token expired. So, we just expire it.
        creds_dict['created'] = now
        creds_dict['expires_in'] = -1
        logging.debug('Creating creds2 using short circuit: %s', creds_dict)
        return Credentials2(**creds_dict)

    # A bug in withings_api doesn't use created to indicate when the token
    # expires, so we have to set it ourselves relative to now.
    #
    # oauthlib.oauth2.rfc6749.clients.base.Client.add_token uses its own
    # "_expires_at" field. It uses "expires_at" if provided directly or it is
    # calculated from "expires_in" based on "now" (withings API relies on this
    # implicit behavior, as it only passes "expires_in.")
    #
    # service_creds includes "created" and "expires_in." The withings API
    # passes "Credentials2.expires_in" directly to oauth via the withing
    # client's "token" dict.
    #
    # As such, when we create a Credentials2, we need to make sure that
    # expires_in is relative to the current time.
    # Calculate the original expires at, that Credentials2 uses for token_expiry
    logging.debug('Creating creds2 starting with: %s', creds_dict)
    expires_at = creds_dict['created'] + datetime.timedelta(
        seconds=creds_dict.get('expires_in', -1)
    )

    # Now frame the token in relation to "now," what OAuth2Session expects.
    creds_dict['created'] = now
    creds_dict['expires_in'] = (expires_at - creds_dict['created']).total_seconds()
    logging.debug('Creating creds2 using: %s', creds_dict)
    return Credentials2(**creds_dict)

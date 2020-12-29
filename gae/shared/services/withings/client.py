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
    service_creds = service['credentials']
    creds = Credentials2(**service_creds)

    def refresh_callback(new_credentials):
        """Updates credentials.

        Params:
            new_credentials: withings_api.Credentials
        """
        logging.debug('Withings creds refresh for: %s', service.key)
        creds_dict = new_credentials.dict(exclude={'created'})
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

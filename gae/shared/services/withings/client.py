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

import nokia

from shared.datastore.service import Service


def create_client(service):
    if not Service.has_credentials(service, required_key='refresh_token'):
        raise Exception('Cannot create Withings client without creds: %s', service)
    # Note: token_expiry is equivelent to expires_at, provided by the API.
    creds = nokia.NokiaCredentials(
        access_token=service['credentials'].get('access_token'),
        token_expiry=service['credentials'].get('expires_at'),
        token_type=service['credentials'].get('token_type'),
        refresh_token=service['credentials'].get('refresh_token'),
        user_id=service['credentials'].get('user_id'),
        client_id=service['credentials'].get('client_id'),
        consumer_secret=service['credentials'].get('consumer_secret'),
    )

    def refresh_callback(new_credentials):
        logging.debug('Withings creds refresh for: %s', service.key)
        Service.update_credentials(service, new_credentials)

    return nokia.NokiaApi(creds, refresh_cb=refresh_callback)

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
    logging.debug('withings.create_client: creds: %s', service['credentials'])
    creds = nokia.NokiaCredentials(
            access_token=service['credentials'].get('access_token'),
            token_expiry=service['credentials'].get('token_expiry'),
            token_type=service['credentials'].get('token_type'),
            refresh_token=service['credentials'].get('refresh_token'),
            user_id=service['credentials'].get('user_id'),
            client_id=service['credentials'].get('client_id'),
            consumer_secret=service['credentials'].get('consumer_secret')
            )
    logging.debug('withings.create_client: nokia_creds: %s', creds)

    def refresh_callback(new_credentials):
        updated_credentials = Service.update_credentials(service, new_credentials)
    return nokia.NokiaApi(creds, refresh_cb=refresh_callback)

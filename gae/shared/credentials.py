
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.oauth2.service_account import Credentials

from shared.config import config

if os.getenv('GAE_ENV', '').startswith('standard'):
    # Production
    credentials = None
else:
    # Local
    credentials = Credentials.from_service_account_file(
            'env/service_keys/python-client-testing.json')
    if getattr(config, 'datastore_emulator_host', None):
        os.environ['DATASTORE_EMULATOR_HOST'] = config.datastore_emulator_host

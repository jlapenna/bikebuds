# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from shared.config import config

import bikebuds_api


class MainTest(unittest.TestCase):
    def setUp(self):
        configuration = bikebuds_api.Configuration()
        configuration.host = config.api_url

        # Configure API key authorization: api_key
        configuration.api_key['key'] = config.python_client_testing_api_key

        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # configuration.api_key_prefix['key'] = 'Bearer'

        # Configure OAuth2 access token for authorization: firebase
        configuration.access_token = 'XYZXYZXYZ'

        self.admin_api = bikebuds_api.AdminApi(bikebuds_api.ApiClient(configuration))
        self.api = bikebuds_api.BikebudsApi(bikebuds_api.ApiClient(configuration))

    def test_profile(self):
        profile = self.api.get_profile()
        self.assertEqual('jlapenna.test.1@gmail.com', profile.user.key.path[0]['name'])
        self.assertEqual(35056021, profile.athlete.properties.id)

    def test_sync(self):
        service = self.api.get_service(name='withings')
        self.assertEqual('jlapenna.test.1@gmail.com', service.key.path[0]['name'])

        result = self.api.sync_service(name='withings')
        self.assertEqual('jlapenna.test.1@gmail.com', result.key.path[0]['name'])

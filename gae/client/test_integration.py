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

import time
import unittest
import warnings

from shared.config import config

import bikebuds_api


class MainTest(unittest.TestCase):
    def setUp(self):
        self._disable_warnings()
        configuration = self._create_configuration()
        self.admin_api = bikebuds_api.AdminApi(bikebuds_api.ApiClient(configuration))
        self.api = bikebuds_api.BikebudsApi(bikebuds_api.ApiClient(configuration))

    def _disable_warnings(self):
        # Due to a python requests design choice, we receive a warning about
        # leaking connection. This is expected and pretty much out of our
        # authority but it can be annoying in tests, hence we suppress the
        # warning. See Issue psf/requests/issues/1882
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning
        )

    def _create_configuration(self):
        configuration = bikebuds_api.Configuration()
        configuration.host = config.api_url

        # Configure API key authorization: api_key
        configuration.api_key['key'] = config.python_client_testing_api_key

        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # configuration.api_key_prefix['key'] = 'Bearer'

        # Configure OAuth2 access token for authorization: firebase
        configuration.access_token = 'XYZXYZXYZ'
        return configuration

    def test_profile(self):
        profile = self.api.get_profile()
        self.assertEqual('jlapenna.test.1@gmail.com', profile.user.key.path[0]['name'])
        self.assertEqual(35056021, profile.athlete.properties.id)

    def test_sync(self):
        service = self.api.get_service(name='withings')
        self.assertEqual('jlapenna.test.1@gmail.com', service.key.path[0]['name'])
        self.assertFalse(service.properties.sync_state.syncing)

        service = self.api.sync_service(name='withings')
        self.assertTrue(
            service.properties.sync_state.syncing,
            'Service should be syncing, was: %s' % (service.properties.sync_state,),
        )

        remaining_sleep = 10
        while service.properties.sync_state.syncing and remaining_sleep > 0:
            remaining_sleep -= 1
            time.sleep(1)
            service = self.api.get_service(name='withings')
        self.assertFalse(
            service.properties.sync_state.syncing,
            'Service should have finished, was: %s' % (service.properties.sync_state,),
        )
        self.assertTrue(
            service.properties.sync_state.successful,
            'Service should have been successful, was: %s'
            % (service.properties.sync_state,),
        )

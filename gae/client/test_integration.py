#!/usr/bin/env python3
#
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

"""Integration testing for bikebuds

Run this script directly from the client virtualenv to get credentials:
  ./gae/client/test_integration.py

Then run it as a unittest.
  ./tools/scripts/run_integration_tests.sh

"""

import time
import unittest
import warnings


import bikebuds_api

import auth_helper


class MainTest(unittest.TestCase):
    def setUp(self):
        self._disable_warnings()
        flow_creds = auth_helper.load_credentials()
        configuration = auth_helper.load_configuration(flow_creds)
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

    def test_profile(self):
        profile = self.api.get_profile()
        self.assertEqual(35056021, profile.athlete.properties.id)

    def test_routes(self):
        self._ensure_service('strava')

        routes = self.api.get_routes()
        ids = [route.properties.id for route in routes]
        self.assertIn(22930717, ids)

    def test_sync_withings(self):
        self._ensure_service('withings')

    def test_sync_strava(self):
        self._ensure_service('strava')

    def _ensure_service(self, name):
        service = self.api.get_service(name=name)
        self.assertFalse(service.properties.sync_state.syncing)

        service = self.api.sync_service(name=name)
        self.assertTrue(
            service.properties.sync_state.syncing,
            'Service should be syncing, was: %s' % (service.properties.sync_state,),
        )

        remaining_sleep = 10
        while service.properties.sync_state.syncing and remaining_sleep > 0:
            remaining_sleep -= 1
            time.sleep(1)
            service = self.api.get_service(name=name)
        self.assertFalse(
            service.properties.sync_state.syncing,
            'Service should have finished, was: %s' % (service.properties.sync_state,),
        )
        self.assertTrue(
            service.properties.sync_state.successful,
            'Sync should have been successful, was: %s'
            % (service.properties.sync_state,),
        )


if __name__ == '__main__':
    auth_helper.fetch_credentials()

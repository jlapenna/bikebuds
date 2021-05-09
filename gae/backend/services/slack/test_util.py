# Copyright 2020 Google Inc. All Rights Reserved.
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

import re
import unittest

from services.slack.testing_util import EXPECTED_URL, route_for_test
from services.slack.util import generate_url


class MainTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_generate_url(self):
        route = route_for_test()

        # Strip out the key params to avoid deailing with it in the expected url.
        url = generate_url(route)
        url = re.sub(r'key=.*?&', '', url)

        expected_url = EXPECTED_URL
        self.assertEqual(url, expected_url)

    def test_generate_url_no_polylines(self):
        route = route_for_test()

        # Strip out polylines to test _generate_url handles it.
        del route['map']['summary_polyline']

        url = generate_url(route)
        self.assertNotIn('enc:', url)

    def test_generate_url_none_polylines(self):
        route = route_for_test()

        # Strip out polylines to test _generate_url handles it.
        route['map']['summary_polyline'] = None

        url = generate_url(route)
        self.assertNotIn('enc:', url)

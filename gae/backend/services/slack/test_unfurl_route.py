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

import unittest

from services.slack.testing_util import route_for_test
from services.slack.unfurl_route import _route_block


class MainTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_route_block(self):
        route = route_for_test()
        block = _route_block({'url': 'https://www.strava.com/routes/10285651'}, route)
        self.assertTrue(block)

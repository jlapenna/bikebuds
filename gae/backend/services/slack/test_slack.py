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

import json
import mock
import unittest

from services.slack import slack
from shared import responses


class MainTest(unittest.TestCase):
    @mock.patch('shared.slack_util.slack_client.chat_unfurl')
    def test_link(self, chat_unfurl_mock):
        event = json.loads(
            """
        {
           "event" : {
              "links" : [
                 {
                    "url" : "https://www.strava.com/routes/23137957",
                    "domain" : "strava.com"
                 }
              ],
              "channel" : "CL2QA9X1C",
              "user" : "UL2NGJARL",
              "type" : "link_shared",
              "message_ts" : "1579378855.001300"
           },
           "token" : "unYFPYx2dZIR4Eb2MwfabpoI",
           "api_app_id" : "AKU8ZGJG1",
           "event_id" : "EvSFJZPZGA",
           "type" : "event_callback",
           "event_time" : 1579378856,
           "authed_users" : [
              "USR4L7ZGW"
           ],
           "team_id" : "TL2DVHG3H"
        }
        """
        )
        chat_unfurl_mock.return_value = {'ok': True}

        result = slack.process_slack_event(event)

        chat_unfurl_mock.assert_called_once()
        self.assertEqual(result, responses.OK)

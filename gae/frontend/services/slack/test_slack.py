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

import json
import mock
import time
import unittest

import flask

from shared import responses

from services.slack import slack


class SlackTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.register_blueprint(slack.module)
        self.app.debug = True
        self.app.testing = True
        self.client = self.app.test_client()

    def _headers(self):
        return {
            'X-Slack-Request-Timestamp': int(time.time()),
            'X-Slack-Signature': 'SLACK_SIGNATURE',
        }

    @mock.patch('services.slack.slack.slack_events_adapter.server.verify_signature')
    def test_slack_challenge_response(self, verify_signature_mock):
        """Verifies the slack adapter returns a challenge response."""
        verify_signature_mock.return_value = True
        challenge = 'CHALLENGE_STRING'
        resp = self.client.post(
            '/events',
            headers=self._headers(),
            json={
                'token': 'unYFPYx2dZIR4Eb2MwfabpoI',
                'type': 'challenge',
                'challenge': challenge,
            },
        )
        # self.assertEqual(resp.status_code, responses.OK.code)
        # self.assertEqual(resp.data.decode('utf-8'), challenge)
        responses.assertResponse(self, (challenge, 200), resp)

    @mock.patch('services.slack.slack.slack_events_adapter.server.verify_signature')
    @mock.patch('shared.task_util._queue_task')
    def test_slack_event(self, _queue_task, verify_signature_mock):
        """Verifies we handle events correctly.

        https://api.slack.com/events/link_shared
        """
        verify_signature_mock.return_value = True
        self.client.post(
            '/events',
            headers=self._headers(),
            json=json.loads(
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
            ),
        )
        _queue_task.assert_called_once()

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

import mock
import unittest

import flask

from google.cloud.datastore.entity import Entity

from shared import ds_util
from shared import responses
from shared import task_util

from services.slack import slack


class SlackTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.register_blueprint(slack.module)
        self.app.testing = True
        self.client = self.app.test_client()

    @mock.patch('main.slack.process_slack_event', return_value=responses.OK)
    def test_process_slack_event_task_valid(self, slack_process_slack_event_mock):
        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', 'slack-E232eq2ee')
        )
        event_entity.update({'event_id': 'EVENT_ID'})

        r = self.client.post(
            '/tasks/event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        slack_process_slack_event_mock.assert_called_once()
        self.assertEqual(r.status_code, responses.OK.code)

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

    @mock.patch('main.slack._process_link_shared', return_value=responses.OK)
    def test_process_link_shared_called(self, slack_process_link_shared_mock):
        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', 'slack-E232eq2ee')
        )
        event_entity.update(LINK_SHARED_EVENT)

        self.client.post(
            '/tasks/event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        # It doesn't matter what code gets returned, since the method returns
        # whatever _process_link_shared returns, which is a mock. Only test
        # that _process_link_shared is called.
        slack_process_link_shared_mock.assert_called_once()

    @mock.patch('main.slack._create_slack_client')
    @mock.patch('main.slack._create_unfurls')
    def test_process_link_shared(self, mock_create_unfurls, mock_slack_client):
        mock_create_unfurls.return_value = {'http://example.com': 'unfurl'}

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', 'slack-E232eq2ee')
        )
        event_entity.update(LINK_SHARED_EVENT)

        r = self.client.post(
            '/tasks/event',
            data=task_util.task_body_for_test(event=event_entity),
        )

        mock_slack_client.assert_called_once()
        responses.assertResponse(self, responses.OK, r)

    @mock.patch('main.slack._create_slack_client')
    @mock.patch('main.slack._create_unfurls')
    def test_process_link_shared_no_unfurls(
        self, mock_create_unfurls, mock_slack_client
    ):
        mock_create_unfurls.return_value = {}

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', 'slack-E232eq2ee')
        )
        event_entity.update(LINK_SHARED_EVENT)

        r = self.client.post(
            '/tasks/event',
            data=task_util.task_body_for_test(event=event_entity),
        )

        mock_slack_client.assert_called_once()
        responses.assertResponse(self, responses.OK_NO_UNFURLS, r)


LINK_SHARED_EVENT = {
    'api_app_id': 'SOME_APP_ID',
    'authed_users': ['SOME_USER_ID'],
    'authorizations': [
        {
            'enterprise_id': None,
            'is_bot': True,
            'is_enterprise_install': False,
            'team_id': 'SOME_TEAM_ID',
            'user_id': 'SOME_USER_ID',
        }
    ],
    'event': {
        'channel': 'SOME_CHANNEL_ID',
        'event_ts': '1619381634.662237',
        'is_bot_user_member': True,
        'links': [
            {
                'domain': 'strava.com',
                'url': 'https://www.strava.com/activities/3040564323',
            }
        ],
        'message_ts': '1619381633.004900',
        'type': 'link_shared',
        'user': 'U01V550PQ5U',
    },
    'event_context': '1-link_shared-SOME_TEAM_ID-SOME_CHANNEL_ID',
    'event_id': 'Ev01V67ECVF0',
    'event_time': 1619381634,
    'is_ext_shared_channel': False,
    'team_id': 'SOME_TEAM_ID',
    'token': 'SOME_TOKEN',
    'type': 'event_callback',
}

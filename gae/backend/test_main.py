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

from google.cloud.datastore.entity import Entity

from shared import ds_util
from shared import responses
from shared import task_util

import main


class MockWorker(object):
    def sync(self):
        pass


class MainTest(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()

    def test_base(self):
        r = self.client.post('/unittest')
        self.assertEqual(r.status_code, responses.OK.code)


class StravaTest(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.maxDiff = 100000000000
        self.client = main.app.test_client()

    @mock.patch('main.StravaEventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_valid_strava(
        self, ds_util_client_get_mock, strava_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'refresh_token': 'validrefreshtoken'}

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', parent=service.key)
        )

        # We pretend a service exists in the event we create.
        ds_util_client_get_mock.return_value = service

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        self.assertEqual(r.status_code, responses.OK.code)
        strava_worker_mock.assert_called_once()


class WithingsTest(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()

    @mock.patch('main.WithingsEventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_valid_withings(
        self, ds_util_client_get_mock, withings_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'withings'))
        service['credentials'] = {'refresh_token': 'validrefreshtoken'}

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', parent=service.key)
        )

        # We pretend a service exists in the event we create.
        ds_util_client_get_mock.return_value = service

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        self.assertEqual(r.status_code, responses.OK.code)
        withings_worker_mock.assert_called_once()

    @mock.patch('main.WithingsEventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_no_service(
        self, ds_util_client_get_mock, withings_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'withings'))
        service['credentials'] = {'refresh_token': 'validrefreshtoken'}

        event_entity = Entity(ds_util.client.key('SubscriptionEvent'))

        # No service!
        ds_util_client_get_mock.return_value = None

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        self.assertEqual(r.status_code, responses.OK_NO_SERVICE.code)
        withings_worker_mock.assert_not_called()

    @mock.patch('main.WithingsEventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_no_credentials(
        self, ds_util_client_get_mock, withings_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'withings'))

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', parent=service.key)
        )

        # We pretend a service exists in the event we create.
        ds_util_client_get_mock.return_value = service

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        self.assertEqual(r.status_code, responses.OK_NO_CREDENTIALS.code)
        withings_worker_mock.assert_not_called()


class SlackTest(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()

    @mock.patch('main.slack.process_slack_event', return_value=responses.OK)
    def test_process_slack_event_task_valid(self, slack_process_slack_event_mock):
        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', 'slack-E232eq2ee')
        )
        event_entity.update({'event_id': 'EVENT_ID'})

        r = self.client.post(
            '/tasks/process_slack_event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        slack_process_slack_event_mock.assert_called_once()
        self.assertEqual(r.status_code, responses.OK.code)

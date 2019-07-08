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
from shared import task_util
from shared.responses import Responses

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
        self.assertEqual(r.status_code, Responses.OK.code)

    @mock.patch('main.strava.EventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_valid_strava(
        self, ds_util_client_get_mock, strava_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'fake': 'XXX'}

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', parent=service.key)
        )

        # We pretend a service exists in the event we create.
        ds_util_client_get_mock.return_value = service

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event_key=event_entity.key),
        )
        self.assertEqual(r.status_code, Responses.OK.code)
        strava_worker_mock.assert_called_once()

    @mock.patch('main.withings.EventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_valid_withings(
        self, ds_util_client_get_mock, withings_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'withings'))
        service['credentials'] = {'fake': 'XXX'}

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', parent=service.key)
        )

        # We pretend a service exists in the event we create.
        ds_util_client_get_mock.return_value = service

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event_key=event_entity.key),
        )
        self.assertEqual(r.status_code, Responses.OK.code)
        withings_worker_mock.assert_called_once()

    @mock.patch('main.withings.EventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_no_service(
        self, ds_util_client_get_mock, withings_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'withings'))
        service['credentials'] = {'fake': 'XXX'}

        event_entity = Entity(ds_util.client.key('SubscriptionEvent'))

        # No service!
        ds_util_client_get_mock.return_value = None

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event_key=event_entity.key),
        )
        self.assertEqual(r.status_code, Responses.OK_NO_SERVICE.code)
        withings_worker_mock.assert_not_called()

    @mock.patch('main.withings.EventsWorker', return_value=MockWorker())
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
            data=task_util.task_body_for_test(event_key=event_entity.key),
        )
        self.assertEqual(r.status_code, Responses.OK_NO_CREDENTIALS.code)
        withings_worker_mock.assert_not_called()

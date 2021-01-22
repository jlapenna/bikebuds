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

import mock
import unittest

import flask

from google.cloud.datastore.entity import Entity

from shared import ds_util
from shared import responses
from shared import task_util
from shared.datastore.service import Service

from services.withings import withings
from services.withings.withings import EventsWorker


class MockWorker(object):
    def sync(self):
        pass


class WithingsTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.register_blueprint(withings.module)
        self.app.testing = True
        self.client = self.app.test_client()

    @mock.patch('shared.task_util.process_weight_trend')
    @mock.patch('shared.services.withings.client.create_client')
    @mock.patch('shared.ds_util.client.delete_multi')
    @mock.patch('shared.ds_util.client.query')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_no_duplicate(
        self,
        ds_util_client_get_mock,
        ds_util_client_put_mock,
        ds_util_client_query_mock,
        ds_util_client_delete_multi_mock,
        withings_create_client_mock,
        process_weight_trend_mock,
    ):
        user = Entity(ds_util.client.key('User', 'someuser'))
        user['preferences'] = {'daily_weight_notif': True}
        service = Entity(ds_util.client.key('Service', 'withings', parent=user.key))
        service['credentials'] = {'refresh_token': 'validrefreshtoken'}

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', 'Event', parent=service.key)
        )
        event_entity.update(
            {
                'event_data': {
                    'startdate': '1',
                    'enddate': '1',
                }
            }
        )

        # There are three gets we need to account for.
        def get_side_effect(key):
            if key.name == 'Event':
                return None
            elif key.name == 'withings':
                return service
            elif key.name == 'someuser':
                return user

        ds_util_client_get_mock.side_effect = get_side_effect

        worker = EventsWorker(service, event_entity)
        worker.sync()

        ds_util_client_put_mock.assert_any_call(event_entity)
        process_weight_trend_mock.assert_called_once()

    @mock.patch('shared.task_util.process_weight_trend')
    @mock.patch('shared.services.withings.client.create_client')
    @mock.patch('shared.ds_util.client.delete_multi')
    @mock.patch('shared.ds_util.client.query')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_discard_duplicate(
        self,
        ds_util_client_get_mock,
        ds_util_client_put_mock,
        ds_util_client_query_mock,
        ds_util_client_delete_multi_mock,
        withings_create_client_mock,
        process_weight_trend_mock,
    ):
        user = Entity(ds_util.client.key('User', 'someuser'))
        user['preferences'] = {'daily_weight_notif': True}
        service = Entity(ds_util.client.key('Service', 'withings', parent=user.key))
        service['credentials'] = {'refresh_token': 'validrefreshtoken'}

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', 'Event', parent=service.key)
        )

        # There are three gets we need to account for.
        def get_side_effect(key):
            if key.name == 'Event':
                return event_entity
            elif key.name == 'withings':
                return service
            elif key.name == 'someuser':
                return user

        ds_util_client_get_mock.side_effect = get_side_effect

        worker = EventsWorker(service, event_entity)
        worker.sync()

        ds_util_client_put_mock.assert_not_called()
        process_weight_trend_mock.assert_not_called()

    @mock.patch('services.withings.withings.EventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_valid_withings(
        self, ds_util_client_get_mock, ds_util_client_put_mock, withings_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'withings'))
        Service._set_defaults(service)
        service['credentials'] = {'refresh_token': 'validrefreshtoken'}
        _setup_service_get_put(
            service, ds_util_client_get_mock, ds_util_client_put_mock
        )

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', parent=service.key)
        )

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        self.assertEqual(r.status_code, responses.OK.code)
        withings_worker_mock.assert_called_once()

    @mock.patch('services.withings.withings.EventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_no_service(
        self, ds_util_client_get_mock, ds_util_client_put_mock, withings_worker_mock
    ):
        _setup_service_get_put(None, ds_util_client_get_mock, ds_util_client_put_mock)

        event_entity = Entity(ds_util.client.key('SubscriptionEvent'))

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        self.assertEqual(r.status_code, responses.OK_NO_SERVICE.code)
        withings_worker_mock.assert_not_called()

    @mock.patch('services.withings.withings.EventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_no_credentials(
        self, ds_util_client_get_mock, ds_util_client_put_mock, withings_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'withings'))
        Service._set_defaults(service)
        _setup_service_get_put(
            service, ds_util_client_get_mock, ds_util_client_put_mock
        )

        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', parent=service.key)
        )

        r = self.client.post(
            '/tasks/process_event',
            data=task_util.task_body_for_test(event=event_entity),
        )
        self.assertEqual(r.status_code, responses.OK_NO_CREDENTIALS.code)
        withings_worker_mock.assert_not_called()


def _setup_service_get_put(service, ds_util_client_get_mock, ds_util_client_put_mock):
    # We pretend a service exists in the event we create.
    ds_util_client_get_mock.return_value = service

    def mock_put_service(entity):
        ds_util_client_get_mock.return_value = service

    ds_util_client_put_mock.side_effect = mock_put_service

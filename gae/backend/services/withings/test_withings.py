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

from google.cloud.datastore.entity import Entity

from shared import ds_util

from services.withings.withings import EventsWorker

import main


class WithingsTest(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()

    @mock.patch('shared.task_util.process_weight_trend')
    @mock.patch('shared.services.withings.client.create_client')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_no_duplicate(
        self,
        ds_util_client_get_mock,
        ds_util_client_put_mock,
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
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_discard_duplicate(
        self,
        ds_util_client_get_mock,
        ds_util_client_put_mock,
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

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

from stravalib.model import Activity

from services.strava.events_worker import EventsWorker
from shared.datastore.subscription import SubscriptionEvent

from shared import ds_util


class MockQuery(object):
    def __init__(self, results):
        self.results = results

    def fetch(self):
        return self.results


class MainTest(unittest.TestCase):
    def setUp(self):
        pass

    @mock.patch('services.strava.events_worker.ClientWrapper')
    @mock.patch('shared.ds_util.client.delete')
    @mock.patch('shared.ds_util.client.delete_multi')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.query')
    @mock.patch('shared.ds_util.client.transaction')
    def test_events_worker(
        self,
        transaction_mock,
        query_mock,
        put_mock,
        delete_multi_mock,
        delete_mock,
        ClientWrapperMock,
    ):
        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'access_token': 'XYZ_TOKEN'}

        query_mock.side_effect = [MockQuery(_test_events()), MockQuery([])]

        client_mock = mock.Mock()
        client_mock.get_activity.side_effect = _activity_generator
        ClientWrapperMock.return_value = client_mock

        worker = EventsWorker(service)
        worker.sync()

        # Ensure we delete the batch.
        self.assertTrue(delete_multi_mock.called)

        # Even though 2120517859 has multiple evens, one is a delete. So we
        # delete it and never fetch it.
        activity_key = ds_util.client.key('Activity', 2120517859, parent=service.key)
        delete_mock.assert_called_once_with(activity_key)

        # And even though 2120517766 has multiple events, we only fetch it
        # once.
        client_mock.get_activity.assert_called_once_with(2120517766)


def _activity_generator(activity_id):
    activity = Activity()
    activity.name = 'Activity ' + str(activity_id)
    activity.id = activity_id
    activity.distance = 10
    activity.moving_time = 200
    activity.elapsed_time = 100
    activity.total_elevation_gain = 300
    return activity


def _test_events():
    service_key = ds_util.client.key('Service', 'strava')
    return [
        SubscriptionEvent.to_entity(
            {
                'aspect_type': 'create',
                'event_time': 1549151210,
                'object_id': 2120517766,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {},
            },
            parent=service_key,
        ),
        SubscriptionEvent.to_entity(
            {
                'aspect_type': 'update',
                'event_time': 1549151212,
                'object_id': 2120517766,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {'title': 'Updated Title'},
            },
            parent=service_key,
        ),
        SubscriptionEvent.to_entity(
            {
                'aspect_type': 'create',
                'event_time': 1549151211,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {},
            },
            parent=service_key,
        ),
        SubscriptionEvent.to_entity(
            {
                'aspect_type': 'update',
                'event_time': 1549151213,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {'title': 'Second Updated Title'},
            },
            parent=service_key,
        ),
        SubscriptionEvent.to_entity(
            {
                'aspect_type': 'delete',
                'event_time': 1549151214,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {},
            },
            parent=service_key,
        ),
    ]

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
from shared.datastore.service import Service

from services.strava import strava


class MockWorker(object):
    def sync(self):
        pass


class StravaTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.register_blueprint(strava.module)
        self.app.testing = True
        self.client = self.app.test_client()
        self.maxDiff = 100000000000

    @mock.patch('services.strava.strava.EventsWorker', return_value=MockWorker())
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    def test_process_event_task_valid_strava(
        self, ds_util_client_get_mock, ds_util_client_put_mock, strava_worker_mock
    ):

        service = Entity(ds_util.client.key('Service', 'strava'))
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
        responses.assertResponse(self, r, responses.OK)
        strava_worker_mock.assert_called_once()


def _setup_service_get_put(service, ds_util_client_get_mock, ds_util_client_put_mock):
    # We pretend a service exists in the event we create.
    ds_util_client_get_mock.return_value = service

    def mock_put_service(entity):
        ds_util_client_get_mock.return_value = service

    ds_util_client_put_mock.side_effect = mock_put_service

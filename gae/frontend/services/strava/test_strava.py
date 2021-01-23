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

from services.strava import strava


class StravaTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.register_blueprint(strava.module)
        self.app.debug = True
        self.app.testing = True
        self.client = self.app.test_client()

    def _create_event(self):
        return {
            "aspect_type": "create",
            "event_time": 1549151211,
            "object_id": 2156802368,
            "object_type": "activity",
            "owner_id": 35056021,
            "subscription_id": 133263,
        }

    @mock.patch('shared.datastore.athlete.Athlete.get_by_id')
    @mock.patch('shared.task_util._post_task_for_dev')
    def test_strava_event_valid(self, _post_task_for_dev_mock, athlete_get_by_id_mock):
        mock_athlete = Entity(ds_util.client.key('Service', 'strava', 'Athlete'))
        athlete_get_by_id_mock.return_value = mock_athlete

        r = self.client.post('/events', json=self._create_event())
        self.assertEqual(r.status_code, responses.OK.code)
        _post_task_for_dev_mock.assert_called_once()

    @mock.patch('shared.datastore.athlete.Athlete.get_by_id', return_value=None)
    @mock.patch('shared.task_util._post_task_for_dev')
    def test_strava_event_unknown_athlete(
        self, _post_task_for_dev_mock, athlete_get_by_id_mock
    ):
        r = self.client.post('/events', json=self._create_event())
        self.assertEqual(r.status_code, responses.OK.code)

        _post_task_for_dev_mock.assert_not_called()

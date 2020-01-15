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
from urllib.parse import urlencode

from google.cloud.datastore.entity import Entity

from shared import ds_util
from shared.config import config
from shared import responses

import main

SERVICE_KEY = 'ahFkZXZ-YmlrZWJ1ZHMtdGVzdHIxCxIEVXNlciISamxhcGVubmFAZ21haWwuY29tDAsSB1NlcnZpY2UiCHdpdGhpbmdzDA'  # noqa: E501


class MainTest(unittest.TestCase):
    def setUp(self):
        main.app.debug = True
        main.app.testing = True
        self.client = main.app.test_client()

    def test_base(self):
        r = self.client.get('/unittest')
        self.assertEqual(r.status_code, responses.OK.code)

    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.task_util.process_event')
    def test_withings_event_valid(self, process_event_mock, ds_util_put_mock):
        query_string = urlencode(
            {
                'sub_secret': config.withings_creds['sub_secret'],
                'service_key': SERVICE_KEY,
            }
        )
        url = '/services/withings/events?%s' % (query_string,)
        r = self.client.post(
            url, data={'startdate': '1532017199', 'enddate': '1532017200', 'appli': '1'}
        )
        self.assertEqual(r.status_code, responses.OK.code)
        ds_util_put_mock.assert_called_once()
        process_event_mock.assert_called_once()

    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.task_util.process_event')
    def test_withings_event_bad_service_key(self, process_event_mock, ds_util_put_mock):
        query_string = urlencode(
            {
                'sub_secret': config.withings_creds['sub_secret'],
                'service_key': "b'12345'",
            }
        )
        url = '/services/withings/events?%s' % (query_string,)
        r = self.client.post(
            url, data={'startdate': '1532017199', 'enddate': '1532017200', 'appli': '1'}
        )
        self.assertEqual(r.status_code, responses.OK_SUB_EVENT_FAILED.code)
        ds_util_put_mock.assert_called_once()
        process_event_mock.assert_not_called()

    @mock.patch('shared.datastore.athlete.Athlete.get_by_id')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.task_util.process_event')
    def test_strava_event_valid(
        self, process_event_mock, ds_util_put_mock, athlete_get_by_id_mock
    ):
        mock_athlete = Entity(ds_util.client.key('Service', 'strava', 'Athlete'))
        athlete_get_by_id_mock.return_value = mock_athlete

        r = self.client.post('/services/strava/events', json=_strava_create_event())
        self.assertEqual(r.status_code, responses.OK.code)
        ds_util_put_mock.assert_called_once()
        process_event_mock.assert_called_once()

    @mock.patch('shared.datastore.athlete.Athlete.get_by_id', return_value=None)
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.task_util.process_event')
    def test_strava_event_unknown_athlete(
        self, process_event_mock, ds_util_put_mock, athlete_get_by_id_mock
    ):
        r = self.client.post('/services/strava/events', json=_strava_create_event())
        self.assertEqual(r.status_code, responses.OK.code)

        # We expect a failure entity to be written and process to not be
        # called.
        ds_util_put_mock.assert_called_once()
        process_event_mock.assert_not_called()


def _strava_create_event():
    return {
        "aspect_type": "create",
        "event_time": 1549151211,
        "object_id": 2156802368,
        "object_type": "activity",
        "owner_id": 35056021,
        "subscription_id": 133263,
    }

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

import json
import mock
import time
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


class WithingsTest(unittest.TestCase):
    def setUp(self):
        main.app.debug = True
        main.app.testing = True
        self.client = main.app.test_client()

    @mock.patch('shared.task_util._post_task_for_dev')
    def test_withings_event_valid(self, _post_task_for_dev_mock):
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
        _post_task_for_dev_mock.assert_called_once()

    @mock.patch('shared.task_util._post_task_for_dev')
    def test_withings_event_bad_service_key(self, _post_task_for_dev_mock):
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
        _post_task_for_dev_mock.assert_not_called()


class StravaTest(unittest.TestCase):
    def setUp(self):
        main.app.debug = True
        main.app.testing = True
        self.client = main.app.test_client()

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

        r = self.client.post('/services/strava/events', json=self._create_event())
        self.assertEqual(r.status_code, responses.OK.code)
        _post_task_for_dev_mock.assert_called_once()

    @mock.patch('shared.datastore.athlete.Athlete.get_by_id', return_value=None)
    @mock.patch('shared.task_util._post_task_for_dev')
    def test_strava_event_unknown_athlete(
        self, _post_task_for_dev_mock, athlete_get_by_id_mock
    ):
        r = self.client.post('/services/strava/events', json=self._create_event())
        self.assertEqual(r.status_code, responses.OK.code)

        _post_task_for_dev_mock.assert_not_called()


class SlackTest(unittest.TestCase):
    def setUp(self):
        main.app.debug = True
        main.app.testing = True
        self.client = main.app.test_client()

    def _headers(self):
        return {
            'X-Slack-Request-Timestamp': int(time.time()),
            'X-Slack-Signature': 'SLACK_SIGNATURE',
        }

    @mock.patch('services.slack.slack.slack_events_adapter.server.verify_signature')
    def test_slack_challenge_response(self, verify_signature_mock):
        """Verifies the slack adapter returns a challenge response."""
        verify_signature_mock.return_value = True
        challenge = 'CHALLENGE_STRING'
        resp = self.client.post(
            '/services/slack/events',
            headers=self._headers(),
            json={
                'token': 'unYFPYx2dZIR4Eb2MwfabpoI',
                'type': 'challenge',
                'challenge': challenge,
            },
        )
        self.assertEqual(resp.status_code, responses.OK.code)
        self.assertEqual(resp.data.decode('utf-8'), challenge)

    @mock.patch('services.slack.slack.slack_events_adapter.server.verify_signature')
    @mock.patch('shared.task_util._post_task_for_dev')
    def test_slack_event(self, _post_task_for_dev, verify_signature_mock):
        """Verifies we handle events correctly.

        https://api.slack.com/events/link_shared
        """
        verify_signature_mock.return_value = True
        self.client.post(
            '/services/slack/events',
            headers=self._headers(),
            json=json.loads(
                """
        {
           "event" : {
              "links" : [
                 {
                    "url" : "https://www.strava.com/routes/23137957",
                    "domain" : "strava.com"
                 }
              ],
              "channel" : "CL2QA9X1C",
              "user" : "UL2NGJARL",
              "type" : "link_shared",
              "message_ts" : "1579378855.001300"
           },
           "token" : "unYFPYx2dZIR4Eb2MwfabpoI",
           "api_app_id" : "AKU8ZGJG1",
           "event_id" : "EvSFJZPZGA",
           "type" : "event_callback",
           "event_time" : 1579378856,
           "authed_users" : [
              "USR4L7ZGW"
           ],
           "team_id" : "TL2DVHG3H"
        }
        """
            ),
        )
        _post_task_for_dev.assert_called_once()

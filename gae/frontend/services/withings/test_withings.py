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

import flask

from shared.config import config
from shared import responses

from services.withings import withings

SERVICE_KEY = 'ahFkZXZ-YmlrZWJ1ZHMtdGVzdHIxCxIEVXNlciISamxhcGVubmFAZ21haWwuY29tDAsSB1NlcnZpY2UiCHdpdGhpbmdzDA'  # noqa: E501


class WithingsTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.register_blueprint(withings.module)
        self.app.debug = True
        self.app.testing = True
        self.client = self.app.test_client()

    @mock.patch('shared.task_util._post_task_for_dev')
    def test_withings_event_valid(self, _post_task_for_dev_mock):
        query_string = urlencode(
            {
                'sub_secret': config.withings_creds['sub_secret'],
                'service_key': SERVICE_KEY,
            }
        )
        url = '/events?%s' % (query_string,)
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
        url = '/events?%s' % (query_string,)
        r = self.client.post(
            url, data={'startdate': '1532017199', 'enddate': '1532017200', 'appli': '1'}
        )
        self.assertEqual(r.status_code, responses.OK_SUB_EVENT_FAILED.code)
        _post_task_for_dev_mock.assert_not_called()

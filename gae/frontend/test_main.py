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

from shared.config import config

import main

SERVICE_KEY = 'ahFkZXZ-YmlrZWJ1ZHMtdGVzdHIxCxIEVXNlciISamxhcGVubmFAZ21haWwuY29tDAsSB1NlcnZpY2UiCHdpdGhpbmdzDA'

class MainTest(unittest.TestCase):

    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()
        #task_util.process_event = lambda event: None

    def test_base(self):
        r = self.client.get('/unittest')
        assert r.status_code == 200

    @mock.patch('shared.task_util.process_event')
    def test_withings_event_valid(self, process_event_mock):
        query_string = urlencode({
                'sub_secret': config.withings_creds['sub_secret'],
                'service_key': SERVICE_KEY,
        })
        url = '/services/withings/events?%s' % (query_string,)
        r = self.client.post(url, data={
            'startdate': '1532017199',
            'enddate': '1532017200',
            'appli': '1'
            })
        assert r.status_code == 200
        assert process_event_mock.called

    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.task_util.process_event')
    def test_withings_event_bad_service_key(self, process_event_mock, ds_util_put_mock):
        query_string = urlencode({
                'sub_secret': config.withings_creds['sub_secret'],
                'service_key': "b'12345'",
        })
        url = '/services/withings/events?%s' % (query_string,)
        r = self.client.post(url, data={
            'startdate': '1532017199',
            'enddate': '1532017200',
            'appli': '1'
            })
        assert r.status_code == 200
        assert not process_event_mock.called
        assert ds_util_put_mock.called

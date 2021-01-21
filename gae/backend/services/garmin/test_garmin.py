# Copyright 2021 Google Inc. All Rights Reserved.
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

from shared import responses
from shared import task_util

from services.garmin import garmin


class ModuleTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.register_blueprint(garmin.module)
        self.app.testing = True
        self.client = self.app.test_client()

        self.app_context = self.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @mock.patch('sync_helper.do')
    def test_do_called(self, sync_helper_do_mock):
        r = self.client.post(
            flask.url_for('garmin.process_livetrack'),
            data=task_util.task_body_for_test(url='http://anyurl'),
        )
        self.assertTrue(sync_helper_do_mock.called)
        self.assertEqual(r.status_code, responses.OK.code)


class LivetrackWorkerTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_bad_url(self):
        worker = garmin.LivetrackWorker(url='http://dummyurl')
        r = worker.sync()
        self.assertEqual(r, responses.OK_INVALID_LIVETRACK)

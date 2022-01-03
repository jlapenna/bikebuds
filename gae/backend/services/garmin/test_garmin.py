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

import json
import mock
import unittest

import flask
from requests import Session, Response

from shared import responses
from shared import task_util
from shared.datastore.track import Track

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
            '/tasks/livetrack',
            data=task_util.task_body_for_test(url='http://anyurl', publish=False),
        )
        self.assertTrue(sync_helper_do_mock.called)
        responses.assertResponse(self, responses.OK, r)


class TrackWorkerTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @mock.patch('shared.task_util._queue_task')
    def test_invalid_url(self, mock_queue_task):
        worker = garmin.TrackWorker(url='http://dummyurl')
        r = worker.sync()
        responses.assertResponse(self, responses.OK_INVALID_LIVETRACK, r)

    @mock.patch('shared.task_util._queue_task')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch.object(Session, 'get')
    def test_failed_info_url(self, mock_session_get, mock_put, mock_queue_task):
        instance = mock.MagicMock(Response)
        instance.status_code = 500
        mock_session_get.return_value = instance

        worker = garmin.TrackWorker(
            url='https://livetrack.garmin.com/session/session-session/token/TOKENTOKEN'
        )
        r = worker.sync()
        responses.assertResponse(self, responses.OK_INVALID_LIVETRACK, r)

        mock_put.assert_called_once()
        track = mock_put.call_args[0][0]
        self.assertEqual(track.get('status'), Track.STATUS_FAILED)

    @mock.patch('shared.task_util._queue_task')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch.object(Session, 'get')
    def test_finished(self, mock_session_get, mock_put, mock_queue_task):
        instance = mock.MagicMock(Response)
        instance.status_code = 200
        instance.json.return_value = INFO_URL_RESPONSE
        mock_session_get.return_value = instance

        worker = garmin.TrackWorker(
            url='https://livetrack.garmin.com/session/session-session/token/TOKENTOKEN'
        )
        r = worker.sync()
        responses.assertResponse(self, responses.OK, r)

        mock_put.assert_called_once()
        track = mock_put.call_args[0][0]
        self.assertEqual(track.get('status'), Track.STATUS_FINISHED)

    @mock.patch('shared.task_util._queue_task')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch.object(Session, 'get')
    def test_404(self, mock_session_get, mock_put, mock_queue_task):
        """Test that a 200 http response, for a track that is unavailable with an in-json status code, is handled."""
        instance = mock.MagicMock(Response)
        instance.status_code = 200
        instance.json.return_value = INFO_URL_RESPONSE_NOT_FOUND
        mock_session_get.return_value = instance

        worker = garmin.TrackWorker(
            url='https://livetrack.garmin.com/session/session-session/token/TOKENTOKEN'
        )
        r = worker.sync()
        responses.assertResponse(self, responses.OK_INVALID_LIVETRACK, r)

        mock_put.assert_called_once()
        track = mock_put.call_args[0][0]
        self.assertEqual(track.get('status'), Track.STATUS_FAILED)


INFO_URL_EXAMPLE = {
    'session': 'session-session',
    'token': 'TOKENTOKEN',
    'url': 'https://livetrack.garmin.com/session/session-session/token/TOKENTOKEN',
}


INFO_URL_RESPONSE = json.loads(
    """
{
   "gcAvatar" : "https://s3.amazonaws.com/garmin-connect-prod/profile_images/bb0d8db1-898e-49ad-be55-899f12c97448-27485245.png",
   "session" : {
      "end" : "2021-04-11T20:28:36.000Z",
      "position" : {
         "lat" : 37.7755344752222,
         "locationName" : "San Francisco",
         "lon" : -122.442552605644
      },
      "publisher" : {
         "connectUserProfileId" : 27485245,
         "identifier" : "A33D5A82-A953-41AE-BD5D-7D7CF45E54DB",
         "nickname" : "JLAPENNA@GMAIL.COM",
         "trackerId" : "UA69B7XL",
         "type" : "WEARABLE"
      },
      "publisherState" : "ACTIVE",
      "sessionId" : "session-session",
      "sessionName" : "04/11/21",
      "start" : "2021-04-11T15:00:09.000Z",
      "subscriber" : {
         "identifier" : "jlapenna.test.1@gmail.com",
         "type" : "EMAIL"
      },
      "subscriberState" : "ACTIVE",
      "token" : "1618153228",
      "url" : "https://livetrack.garmin.com/session/session-session/token/TOKENTOKEN",
      "userDisplayName" : "Joe LaPenna",
      "viewable" : "2021-04-11T20:28:36.000Z"
   },
   "shortened" : false,
   "unitId" : 3996815102,
   "viewable" : false
}
"""
)

INFO_URL_ONGOING = json.loads(
    """
{
   "info" : {
      "gcAvatar" : "https://s3.amazonaws.com/garmin-connect-prod/profile_images/bb0d8db1-898e-49ad-be55-899f12c97448-27485245.png",
      "session" : {
         "end" : "2021-04-11T20:28:36.000Z",
         "position" : {
            "lat" : 37.7755344752222,
            "locationName" : "San Francisco",
            "lon" : -122.442552605644
         },
         "publisher" : {
            "connectUserProfileId" : 27485245,
            "identifier" : "A33D5A82-A953-41AE-BD5D-7D7CF45E54DB",
            "nickname" : "JLAPENNA@GMAIL.COM",
            "trackerId" : "UA69B7XL",
            "type" : "WEARABLE"
         },
         "publisherState" : "ACTIVE",
         "sessionId" : "a0da59fb-7746-46a7-9ea7-af91f499db4a",
         "sessionName" : "04/11/21",
         "start" : "2021-04-11T15:00:09.000Z",
         "subscriber" : {
            "identifier" : "jlapenna.test.1@gmail.com",
            "type" : "EMAIL"
         },
         "subscriberState" : "ACTIVE",
         "token" : "1618153228",
         "url" : "https://livetrack.garmin.com/session/a0da59fb-7746-46a7-9ea7-af91f499db4a/token/C3959988CED14CD664FD3A273BE6E5B4",
         "userDisplayName" : "Joe LaPenna",
         "viewable" : "2021-04-11T20:28:36.000Z"
      },
      "shortened" : false,
      "unitId" : 3996815102,
      "viewable" : false
   },
   "status" : 1,
   "url" : "https://livetrack.garmin.com/session/a0da59fb-7746-46a7-9ea7-af91f499db4a/token/C3959988CED14CD664FD3A273BE6E5B4",
   "url_info" : {
      "session" : "a0da59fb-7746-46a7-9ea7-af91f499db4a",
      "token" : "C3959988CED14CD664FD3A273BE6E5B4"
   }
}

"""
)


INFO_URL_RESPONSE_NOT_FOUND = json.loads(
    """
{
   "statusCode" : 404
}
"""
)

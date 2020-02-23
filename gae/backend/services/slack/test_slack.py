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

import json
import mock
import unittest

from google.cloud.datastore.entity import Entity

from shared import ds_util
from shared import responses

from services.slack import slack
from services.slack.testutil import (
    activity_entity_for_test,
    route_generator,
    set_mockurlopen,
)


class MainTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @mock.patch('shared.slack_util.slack_client.chat_unfurl')
    @mock.patch('services.slack.slack.ClientWrapper')
    @mock.patch('shared.ds_util.client.get')
    def test_route_link(
        self, ds_util_client_get_mock, ClientWrapperMock, chat_unfurl_mock
    ):
        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'access_token': 'validrefreshtoken'}
        ds_util_client_get_mock.return_value = service

        client_mock = mock.Mock()
        client_mock.get_route.side_effect = route_generator
        ClientWrapperMock.return_value = client_mock

        chat_unfurl_mock.return_value = {'ok': True}

        event = json.loads(
            """
            {
               "event_id" : "EvSFJZPZGA",
               "token" : "unYFPYx2dZIR4Eb2MwfabpoI",
               "authed_users" : [
                  "USR4L7ZGW"
               ],
               "event_time" : 1579378856,
               "type" : "event_callback",
               "event" : {
                  "channel" : "CL2QA9X1C",
                  "links" : [
                     {
                        "domain" : "strava.com",
                        "url" : "https://www.strava.com/routes/10285651"
                     }
                  ],
                  "user" : "UL2NGJARL",
                  "message_ts" : "1579378855.001300",
                  "type" : "link_shared"
               },
               "team_id" : "TL2DVHG3H",
               "api_app_id" : "AKU8ZGJG1"
            }
        """
        )
        result = slack.process_slack_event(event)

        chat_unfurl_mock.assert_called_once()
        self.assertEqual(result, responses.OK)

    @mock.patch('shared.slack_util.slack_client.chat_unfurl')
    @mock.patch('shared.ds_util.client.query')
    @mock.patch('shared.ds_util.client.get')
    def disabled_test_datastore_activity_link(
        self, ds_util_client_get_mock, ds_util_client_query_mock, chat_unfurl_mock,
    ):
        """Disabled: We currently dont fetch activities from the datastore."""
        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'access_token': 'validrefreshtoken'}
        ds_util_client_get_mock.return_value = service

        query_mock = mock.Mock()
        query_mock.add_filter.return_value = None
        query_mock.fetch.return_value = [activity_entity_for_test(3046711547)]
        ds_util_client_query_mock.return_value = query_mock

        chat_unfurl_mock.return_value = {'ok': True}

        event = json.loads(
            """
            {
               "event_id" : "EvSFJZPZGA",
               "token" : "unYFPYx2dZIR4Eb2MwfabpoI",
               "authed_users" : [
                  "USR4L7ZGW"
               ],
               "event_time" : 1579378856,
               "type" : "event_callback",
               "event" : {
                  "channel" : "CL2QA9X1C",
                  "links" : [
                     {
                        "domain" : "strava.com",
                        "url" : "https://www.strava.com/activities/3046711547"
                     }
                  ],
                  "user" : "UL2NGJARL",
                  "message_ts" : "1579378855.001300",
                  "type" : "link_shared"
               },
               "team_id" : "TL2DVHG3H",
               "api_app_id" : "AKU8ZGJG1"
            }
        """
        )
        result = slack.process_slack_event(event)

        chat_unfurl_mock.assert_called_once()
        self.assertEqual(result, responses.OK)

    @mock.patch('shared.slack_util.slack_client.chat_unfurl')
    @mock.patch('urllib.request.urlopen')
    @mock.patch('shared.services.strava.client.ClientWrapper')
    @mock.patch('shared.ds_util.client.query')
    @mock.patch('shared.ds_util.client.get')
    def test_crawled_activity_link(
        self,
        ds_util_client_get_mock,
        ds_util_client_query_mock,
        ClientWrapperMock,
        mock_urlopen,
        chat_unfurl_mock,
    ):
        """Tests that we crawl the url if we don't have it in the DB."""
        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'access_token': 'validrefreshtoken'}
        ds_util_client_get_mock.return_value = service

        query_mock = mock.Mock()
        query_mock.add_filter.return_value = None
        query_mock.fetch.return_value = []
        ds_util_client_query_mock.return_value = query_mock

        set_mockurlopen(mock_urlopen)

        chat_unfurl_mock.return_value = {'ok': True}

        event = json.loads(
            """
            {
               "event_id" : "EvSFJZPZGA",
               "token" : "unYFPYx2dZIR4Eb2MwfabpoI",
               "authed_users" : [
                  "USR4L7ZGW"
               ],
               "event_time" : 1579378856,
               "type" : "event_callback",
               "event" : {
                  "channel" : "CL2QA9X1C",
                  "links" : [
                     {
                        "domain" : "strava.com",
                        "url" : "https://www.strava.com/activities/3046711547"
                     }
                  ],
                  "user" : "UL2NGJARL",
                  "message_ts" : "1579378855.001300",
                  "type" : "link_shared"
               },
               "team_id" : "TL2DVHG3H",
               "api_app_id" : "AKU8ZGJG1"
            }
        """
        )
        result = slack.process_slack_event(event)

        chat_unfurl_mock.called_once()
        self.assertEqual(result, responses.OK)

    @mock.patch('urllib.request.urlopen')
    def test_resolve_rewrite_link_url(self, mock_urlopen):
        set_mockurlopen(mock_urlopen)

        link = {'domain': 'strava.app.link', 'url': 'https://strava.app.link/234141243'}
        url = slack._resolve_rewrite_link(link)
        self.assertEqual(url, 'https://www.strava.com/activities/3123195350')

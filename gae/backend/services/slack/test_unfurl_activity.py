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

import mock
import unittest

from google.cloud.datastore.entity import Entity

from shared import ds_util

from services.slack.testing_util import (
    activity_entity_for_test,
    set_mockurlopen,
    MOCK_CRAWLED_ACTIVITY,
)
from services.slack.unfurl_activity import (
    _api_activity_block,
    _crawled_activity_block,
    _unfurl_activity_from_crawl,
    _unfurl_activity_from_datastore,
    unfurl_activity,
)


class MainTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_api_activity_block(self):
        activity = activity_entity_for_test(11111)
        block = _api_activity_block(
            {'url': 'https://www.strava.com/activities/11111'}, activity
        )
        self.assertTrue(block)

    def test_api_activity_block_with_primary_photo(self):
        activity = activity_entity_for_test(11111, with_photo=True)
        block = _api_activity_block(
            {'url': 'https://www.strava.com/activities/11111'}, activity
        )
        self.assertTrue(block)

    @mock.patch('urllib.request.urlopen')
    def test_unfurl_activity(self, mock_urlopen):
        set_mockurlopen(mock_urlopen)

        url = 'https://www.strava.com/activities/3123195350'
        activity_block = unfurl_activity(None, url)

        expected = {
            'blocks': [
                {
                    'accessory': {
                        'alt_text': 'activity image',
                        'image_url': 'https://dgtzuqphqg23d.cloudfront.net/q1ixMRMczt82TG8EZDC1bvQioVWD8a-pJsadS0C14Ro-768x575.jpg',
                        'type': 'image',
                    },
                    'text': {
                        'text': '<https://www.strava.com/activities/3123195350|*Choo '
                        "choo - Joe LaPenna's 48.3 mi bike ride*>\n",
                        'type': 'mrkdwn',
                    },
                    'type': 'section',
                },
                {'type': 'divider'},
                {
                    'fields': [
                        {'text': '*Distance:* 48.3mi', 'type': 'mrkdwn'},
                        {'text': '*Speed:* 13.0mph', 'type': 'mrkdwn'},
                    ],
                    'type': 'section',
                },
            ]
        }
        self.assertDictEqual(dict(activity_block), expected)

    @mock.patch('urllib.request.urlopen')
    def test_unfurl_from_crawl(self, mock_urlopen):
        set_mockurlopen(mock_urlopen)

        url = 'https://www.strava.com/activities/3123195350'
        activity_block = _unfurl_activity_from_crawl(url)

        expected = {
            'blocks': [
                {
                    'accessory': {
                        'alt_text': 'activity image',
                        'image_url': 'https://dgtzuqphqg23d.cloudfront.net/q1ixMRMczt82TG8EZDC1bvQioVWD8a-pJsadS0C14Ro-768x575.jpg',
                        'type': 'image',
                    },
                    'text': {
                        'text': '<https://www.strava.com/activities/3123195350|*Choo '
                        "choo - Joe LaPenna's 48.3 mi bike ride*>\n",
                        'type': 'mrkdwn',
                    },
                    'type': 'section',
                },
                {'type': 'divider'},
                {
                    'fields': [
                        {'text': '*Distance:* 48.3mi', 'type': 'mrkdwn'},
                        {'text': '*Speed:* 13.0mph', 'type': 'mrkdwn'},
                    ],
                    'type': 'section',
                },
            ]
        }
        self.assertDictEqual(dict(activity_block), expected)

    def test_unfurl_from_datastore(self):
        client_mock = mock.Mock()

        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'access_token': 'validrefreshtoken'}
        client_mock.return_value = service

        query_mock = mock.Mock()
        query_mock.add_filter.return_value = None
        query_mock.fetch.return_value = [activity_entity_for_test(3046711547)]
        client_mock.query.return_value = query_mock

        url = 'https://www.strava.com/activities/3123195350'
        activity_block = _unfurl_activity_from_datastore(client_mock, url)

        # This strips the API key, so we have to strip it from the expected output, too; for reasonable comparisons.
        if activity_block.get('blocks', [{}])[0].get('accessory', {}).get('image_url'):
            activity_block['blocks'][0]['accessory']['image_url'] = 'XYZ_URL'

        # This strips the API key, so we have to strip it from the actual output, too; for reasonable comparisons.
        expected = {
            'blocks': [
                {
                    'accessory': {
                        'alt_text': 'route map',
                        'image_url': 'XYZ_URL',
                        'type': 'image',
                    },
                    'text': {
                        'text': '<https://www.strava.com/activities/3123195350|*Activity '
                        '3046711547*> by '
                        '<https://www.strava.com/athletes/111|ActivityFirstName '
                        'ActivityLastName>, August 23, 2017\n'
                        'Description: 3046711547',
                        'type': 'mrkdwn',
                    },
                    'type': 'section',
                },
                {'type': 'divider'},
                {
                    'fields': [
                        {'text': '*Distance:* 0.01mi', 'type': 'mrkdwn'},
                        {'text': '*Elevation:* 984.0ft', 'type': 'mrkdwn'},
                    ],
                    'type': 'section',
                },
            ]
        }
        self.assertDictEqual(dict(activity_block), expected)

    def test_crawled_activity_block(self):
        block = _crawled_activity_block(
            {'url': 'https://www.strava.com/activities/11111'}, MOCK_CRAWLED_ACTIVITY
        )
        expected_block = {
            'blocks': [
                {
                    'accessory': {
                        'alt_text': 'activity image',
                        'image_url': 'http://d3nn82uaxijpm6.cloudfront.net/assets/sharing/summary_activity_generic-ec8c36660493881ac5fb7b7.png',
                        'type': 'image',
                    },
                    'text': {
                        'text': "<{'url': "
                        "'https://www.strava.com/activities/11111'}|*Morning "
                        "Ride - Bob Stover's 58.0 mi bike ride*>\n"
                        'Bob S. rode 58.0 mi on Apr 24, 2021.',
                        'type': 'mrkdwn',
                    },
                    'type': 'section',
                },
                {'type': 'divider'},
                {
                    'fields': [
                        {'text': '*Distance:* 58.1mi', 'type': 'mrkdwn'},
                        {'text': '*Speed:* 15.0mph', 'type': 'mrkdwn'},
                    ],
                    'type': 'section',
                },
            ]
        }
        self.assertEqual(block, expected_block)

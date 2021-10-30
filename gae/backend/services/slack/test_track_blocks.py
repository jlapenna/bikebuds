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

import unittest

from services.slack.testing_util import (
    track_finished_for_test,
)
from services.slack.track_blocks import (
    create_track_blocks,
)


class MainTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_track_finished(self):
        track = track_finished_for_test()
        track_blocks = create_track_blocks(track)
        expected = [
            {
                'text': {
                    'text': "<https://livetrack.garmin.com/session/session-session/token/TOKENTOKEN|*Joe LaPenna's Ride*>",
                    'type': 'mrkdwn',
                },
                'accessory': {
                    'alt_text': 'avatar image',
                    'image_url': 'https://s3.amazonaws.com/garmin-connect-prod/profile_images/avatar.png',
                    'type': 'image',
                },
                'type': 'section',
            },
            {
                'elements': [
                    {'text': '*Location:* San Francisco', 'type': 'mrkdwn'},
                    {'text': '*Started:* 2021-04-11 15:00:00+00:00', 'type': 'mrkdwn'},
                ],
                'type': 'context',
            },
        ]
        self.assertListEqual(track_blocks, expected)

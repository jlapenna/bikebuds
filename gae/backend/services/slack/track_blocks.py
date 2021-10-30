# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional

from google.cloud.datastore.entity import Entity


def create_track_blocks(track: Entity) -> Optional[list]:
    url = track['url']
    title = f"{track['info']['session']['userDisplayName']}'s Ride"
    avatar_img = track['info']['gcAvatar']
    location = track['info']['session']['position']['locationName']
    started = track['start']
    blocks = [
        {
            'text': {
                'text': f"<{url}|*{title}*>",
                'type': 'mrkdwn',
            },
            'accessory': {
                'alt_text': 'avatar image',
                'image_url': avatar_img,
                'type': 'image',
            },
            'type': 'section',
        },
        {
            'elements': [
                {'text': f'*Location:* {location}', 'type': 'mrkdwn'},
                {'text': f'*Started:* {started}', 'type': 'mrkdwn'},
            ],
            'type': 'context',
        },
    ]
    return blocks

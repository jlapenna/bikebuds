# Copyright 2020 Google LLC
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

ROUTE_BLOCK = r"""
{
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<%(url)s|*%(name)s*> by <https://www.strava.com/athletes/%(athlete.id)s|%(athlete.firstname)s %(athlete.lastname)s>\n%(description)s\n\nCreated on %(timestamp)s"
            },
            "accessory": {
                "type": "image",
                "image_url": "%(map_image_url)s",
                "alt_text": "route map"
            }
        }
    ]
}
"""

API_ACTIVITY_BLOCK = r"""
{
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<%(url)s|*%(name)s*> by <https://www.strava.com/athletes/%(athlete.id)s|%(athlete.firstname)s %(athlete.lastname)s>, %(timestamp)s\n%(description)s"
            },
            "accessory": {
                "type": "image",
                "image_url": "%(map_image_url)s",
                "alt_text": "route map"
            }
        }
    ]
}
"""

CRAWLED_ACTIVITY_BLOCK = r"""
{
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<%(url)s|*%(title)s*>\n%(description)s"
            },
            "accessory": {
                "type": "image",
                "image_url": "%(image_url)s",
                "alt_text": "activity image"
            }
        }
    ]
}
"""

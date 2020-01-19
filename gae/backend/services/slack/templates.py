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

ROUTE_BLOCK = """
{
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<https://www.strava.com/route/%(id)s|*%(name)s*> by <https://www.strava.com/athletes/%(athlete.id)s|%(athlete.firstname)s %(athlete.lastname)s>\\n%(description)s\\nCreated on %(created)s"
            },
            "accessory": {
                "type": "image",
                "image_url": "%(map_image_url)s",
                "alt_text": "route map"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Distance:* %(distance)s"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Elevation:* %(elevation_gain)s"
                }
            ]
        }
    ]
}
"""

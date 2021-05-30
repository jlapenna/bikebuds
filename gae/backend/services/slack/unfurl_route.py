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

import logging

from babel.dates import format_date
from measurement.measures import Distance
from stravalib import exc

from shared.datastore.route import Route
from services.slack.util import get_id, generate_url


def unfurl_route(client, url):
    route_id = get_id(url)
    try:
        route = client.get_route(route_id)
    except exc.ObjectNotFound:
        logging.debug('Unknown Route: {route_id}')
        return None
    route_entity = Route.to_entity(route)
    return {'blocks': _route_blocks(url, route_entity)}


def _route_blocks(url, route):
    route_sub = {
        'id': route['id'],
        'timestamp': format_date(route['timestamp'], format='medium'),
        'description': route['description'],
        'name': route['name'],
        'athlete.id': route['athlete']['id'],
        'athlete.firstname': route['athlete']['firstname'],
        'athlete.lastname': route['athlete']['lastname'],
        'url': url,
    }
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<%(url)s|*%(name)s*> by <https://www.strava.com/athletes/%(athlete.id)s|%(athlete.firstname)s %(athlete.lastname)s>\n%(description)s\n\nCreated on %(timestamp)s"
                % route_sub,
            },
            "accessory": {
                "type": "image",
                "image_url": generate_url(route),
                "alt_text": "route map",
            },
        }
    ]

    fields = []
    if route.get('distance', None):
        fields.append(
            {
                "type": "mrkdwn",
                "text": "*Distance:* %smi" % round(Distance(m=route['distance']).mi, 2),
            }
        )

    if route.get('elevation_gain', None):
        fields.append(
            {
                "type": "mrkdwn",
                "text": "*Elevation:* %sft"
                % round(Distance(m=route['elevation_gain']).ft, 0),
            }
        )

    if fields:
        blocks.append({"type": "divider"})
        blocks.append({"type": "section", "fields": fields})
    return blocks

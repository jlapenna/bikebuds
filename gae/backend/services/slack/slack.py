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

import json
import logging
import urllib

from babel.dates import format_date
from measurement.measures import Distance

from services.slack.templates import ROUTE_BLOCK
from services.strava.client import ClientWrapper
from shared import responses
from shared.config import config
from shared.datastore.bot import Bot
from shared.datastore.route import Route
from shared.datastore.service import Service
from shared.slack_util import slack_client


def process_slack_event(event):
    """Procesess an event.

    Args:
        event: An entity representing a full event message, including event_id, etc.
    """
    logging.debug('process_slack_event: %s', event)
    if event['event']['type'] == 'link_shared':
        return process_link_shared(event)
    return responses.OK_SUB_EVENT_UNKNOWN


def process_link_shared(event):
    service = Service.get('strava', parent=Bot.key())
    client = ClientWrapper(service)
    unfurls = dict(
        (link['url'], _unfurl(client, link)) for link in event['event']['links']
    )
    response = slack_client.chat_unfurl(
        channel=event['event']['channel'],
        ts=event['event']['message_ts'],
        unfurls=unfurls,
    )
    if not response['ok']:
        logging.error('process_link_shared: failed: %s with %s', response, unfurls)
        return responses.INTERNAL_SERVER_ERROR
    logging.debug('process_link_shared: %s', response)
    return responses.OK


def _unfurl(client, link):
    if '/routes/' in link['url']:
        url = urllib.parse.urlparse(link['url'])
        route = client.get_route(url.path.split('/')[-1])
        route = Route.to_entity(route)
        return _route_block(route)


def _route_block(route):
    route_sub = {
        'id': route['id'],
        'timestamp': format_date(route['timestamp'], format='medium'),
        'description': route['description'],
        'distance': round(Distance(m=route['distance']).mi, 2),
        'elevation_gain': round(Distance(m=route['elevation_gain']).ft),
        'name': route['name'],
        'athlete.id': route['athlete']['id'],
        'athlete.firstname': route['athlete']['firstname'],
        'athlete.lastname': route['athlete']['lastname'],
        'map_image_url': _generate_url(route),
    }
    return json.loads(ROUTE_BLOCK % route_sub)


def _generate_url(route):
    url = 'https://maps.googleapis.com/maps/api/staticmap?'
    params = {
        'key': config.api_key,
        'size': '512x512',
        'maptype': 'roadmap',
        'path': 'enc:' + route['map']['summary_polyline'],
        'format': 'jpg',
    }
    return url + urllib.parse.urlencode(params)

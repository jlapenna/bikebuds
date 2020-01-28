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

from services.slack.templates import ACTIVITY_BLOCK, ROUTE_BLOCK
from shared.services.strava.client import ClientWrapper
from shared import responses
from shared.config import config
from shared.datastore.bot import Bot
from shared.datastore.route import Route
from shared.datastore.service import Service
from shared import ds_util
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
    unfurls = {}
    for link in event['event']['links']:
        unfurl = _unfurl(client, link)
        if unfurl:
            unfurls[link['url']] = unfurl
    if not unfurls:
        return responses.OK

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
        route_id = _get_id(link)
        route = client.get_route(route_id)
        route_entity = Route.to_entity(route)
        return _route_block(link['url'], route_entity)
    elif '/activities/' in link['url']:
        activity_id = _get_id(link)
        activities_query = ds_util.client.query(kind='Activity')
        activities_query.add_filter('id', '=', activity_id)
        all_activities = [a for a in activities_query.fetch()]

        if all_activities:
            activity_entity = all_activities[0]
            if activity_entity.get('private'):
                return None
            return _activity_block(link['url'], activity_entity)
        else:
            return None


def _get_id(link):
    url = urllib.parse.urlparse(link['url'])
    return int(url.path.split('/')[-1])


def _route_block(url, route):
    route_sub = {
        'id': route['id'],
        'timestamp': format_date(route['timestamp'], format='medium'),
        'description': route['description'],
        'name': route['name'],
        'athlete.id': route['athlete']['id'],
        'athlete.firstname': route['athlete']['firstname'],
        'athlete.lastname': route['athlete']['lastname'],
        'map_image_url': _generate_url(route),
        'url': url,
    }
    unfurl = json.loads(ROUTE_BLOCK % route_sub)

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
        unfurl['blocks'].append({"type": "divider"})
        unfurl['blocks'].append({"type": "section", "fields": fields})
    return unfurl


def _activity_block(url, activity):
    activity_sub = {
        'id': activity['id'],
        'timestamp': format_date(activity['start_date'], format='long'),
        'description': activity['description'],
        'name': activity['name'],
        'athlete.id': activity['athlete']['id'],
        'athlete.firstname': activity['athlete']['firstname'],
        'athlete.lastname': activity['athlete']['lastname'],
        'map_image_url': _generate_url(activity),
        'url': url,
    }
    unfurl = json.loads(ACTIVITY_BLOCK % activity_sub)

    fields = []
    if activity.get('distance', None):
        fields.append(
            {
                "type": "mrkdwn",
                "text": "*Distance:* %smi"
                % round(Distance(m=activity['distance']).mi, 2),
            }
        )

    if activity.get('total_elevation_gain', None):
        fields.append(
            {
                "type": "mrkdwn",
                "text": "*Elevation:* %sft"
                % round(Distance(m=activity['total_elevation_gain']).ft, 0),
            }
        )

    if fields:
        unfurl['blocks'].append({"type": "divider"})
        unfurl['blocks'].append({"type": "section", "fields": fields})

    try:
        primary_image = activity['photos']['primary']['urls']['600']
    except (KeyError, TypeError):
        primary_image = None
    if primary_image:
        unfurl['blocks'].append(
            {"type": "image", "image_url": primary_image, "alt_text": "Cover Photo"}
        )
    return unfurl


def _generate_url(route):
    url = 'https://maps.googleapis.com/maps/api/staticmap?'
    params = {
        'key': config.firebase_web_creds['apiKey'],
        'size': '512x512',
        'maptype': 'roadmap',
        'path': 'enc:' + route['map']['summary_polyline'],
        'format': 'jpg',
    }
    return url + urllib.parse.urlencode(params)

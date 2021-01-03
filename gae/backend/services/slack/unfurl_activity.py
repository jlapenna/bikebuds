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
import urllib.request

from babel.dates import format_date
from bs4 import BeautifulSoup
from measurement.measures import Distance, Speed
from measurement.utils import guess

from services.slack.templates import (
    API_ACTIVITY_BLOCK,
    CRAWLED_ACTIVITY_BLOCK,
)
from services.slack.util import get_id, generate_url


def unfurl_activity(client, url):
    return _unfurl_activity_from_crawl(url)


def _unfurl_activity_from_crawl(url):
    activity = _fetch_parse_activity_url(url)
    if not activity:
        return
    return _crawled_activity_block(url, activity)


def _unfurl_activity_from_datastore(client, url):
    activity_id = get_id(url)
    activities_query = client.query(kind='Activity')
    activities_query.add_filter('id', '=', activity_id)
    all_activities = [a for a in activities_query.fetch()]

    if not all_activities:
        return

    activity_entity = all_activities[0]
    if activity_entity.get('private'):
        return None
    return _api_activity_block(url, activity_entity)


def _api_activity_block(url, activity):
    activity_sub = {
        'id': activity['id'],
        'timestamp': format_date(activity['start_date'], format='long'),
        'name': activity['name'],
        'description': activity['description'],
        'athlete.id': activity['athlete']['id'],
        'athlete.firstname': activity['athlete']['firstname'],
        'athlete.lastname': activity['athlete']['lastname'],
        'map_image_url': generate_url(activity),
        'url': url,
    }
    unfurl = json.loads(API_ACTIVITY_BLOCK % activity_sub)

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

    if activity.get('average_speed', None):
        fields.append(
            {
                "type": "mrkdwn",
                "text": "*Speed:* %smph"
                % round(Speed(m__s=activity['average_speed']).mph, 0),
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


def _fetch_parse_activity_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            contents = response.read()
    except urllib.request.HTTPError:
        logging.exception('Could not fetch %s', url)
        return None

    soup = BeautifulSoup(contents, 'html.parser')
    metas = soup.find_all('meta', property=True, content=True)
    return dict((meta['property'], meta['content']) for meta in metas)


def _crawled_activity_block(url, activity):
    if 'og:title' not in activity:
        return
    title = activity['og:title']

    if 'twitter:title' not in activity:
        return
    name = activity['twitter:title']

    if 'og:description' not in activity:
        return
    description = activity['og:description']

    if 'og:image' not in activity:
        return
    image = activity['og:image']

    activity_sub = {
        'title': title,
        'name': name,
        'description': description,
        'url': url,
        'image_url': image,
    }
    unfurl = json.loads(CRAWLED_ACTIVITY_BLOCK % activity_sub)

    fields = []
    if 'fitness:distance:value' in activity:
        distance = guess(
            activity['fitness:distance:value'],
            activity['fitness:distance:units'],
            [Distance],
        )
        fields.append(
            {
                "type": "mrkdwn",
                "text": "*Distance:* %smi" % round(distance.mi, 2),
            }
        )

    if 'fitness:speed:value' in activity:
        average_speed = guess(
            activity['fitness:speed:value'],
            activity['fitness:speed:units'].replace('/', '__'),
            [Speed],
        )
        fields.append(
            {
                "type": "mrkdwn",
                "text": "*Speed:* %smph" % round(average_speed.mph, 0),
            }
        )

    if fields:
        unfurl['blocks'].append({"type": "divider"})
        unfurl['blocks'].append({"type": "section", "fields": fields})

    return unfurl

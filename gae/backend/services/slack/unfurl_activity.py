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
import urllib
import urllib.request

from babel.dates import format_date
from bs4 import BeautifulSoup
from measurement.measures import Distance, Speed
from measurement.utils import guess

from services.slack.util import get_id, generate_url


def unfurl_activity(client, url):
    return _unfurl_activity_from_crawl(url)


def _unfurl_activity_from_crawl(url):
    activity = _fetch_parse_activity_url(url)
    if not activity:
        logging.warn(f'Unable to crawl url {url}')
        return
    logging.debug(f'{activity}')
    blocks = _crawled_activity_blocks(url, activity)
    logging.debug(f'{blocks}')
    if not blocks:
        logging.warn(f'Unable to parse {activity} for {url}')
    return {'blocks': blocks}


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
    blocks = _api_activity_blocks(url, activity_entity)
    if not blocks:
        logging.warn(f'Unable to parse {activity_entity} for {url}')
    return {'blocks': blocks}


def _api_activity_blocks(url, activity):
    activity_sub = {
        'id': activity['id'],
        'timestamp': format_date(activity['start_date'], format='long'),
        'name': activity['name'],
        'description': activity['description'],
        'athlete.id': activity['athlete']['id'],
        'athlete.firstname': activity['athlete']['firstname'],
        'athlete.lastname': activity['athlete']['lastname'],
        'url': url,
    }
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<%(url)s|*%(name)s*> by <https://www.strava.com/athletes/%(athlete.id)s|%(athlete.firstname)s %(athlete.lastname)s>, %(timestamp)s\n%(description)s"
                % activity_sub,
            },
            "accessory": {
                "type": "image",
                "image_url": generate_url(activity),
                "alt_text": "route map",
            },
        }
    ]

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
        blocks.append({"type": "divider"})
        blocks.append({"type": "section", "fields": fields})

    try:
        primary_image = activity['photos']['primary']['urls']['600']
    except (KeyError, TypeError):
        primary_image = None
    if primary_image:
        blocks.append(
            {"type": "image", "image_url": primary_image, "alt_text": "Cover Photo"}
        )
    return blocks


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


def _crawled_activity_blocks(url, activity):
    title = None
    if 'og:title' in activity:
        title = activity['og:title']
    elif 'twitter:title' not in activity:
        title = activity['twitter:title']

    description = None
    if 'og:description' in activity:
        description = activity['og:description']
    elif 'twitter:description' in activity:
        description = activity['twitter:description']

    image_url = None
    if 'og:image' in activity:
        image_url = activity['og:image']
    elif 'twitter:image' not in activity:
        image_url = activity['twitter:image']

    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"<{url}|*{title}*>\n{description}"},
            "accessory": {
                "type": "image",
                "image_url": image_url,
                "alt_text": "activity image",
            },
        }
    ]

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
        blocks.append({"type": "divider"})
        blocks.append({"type": "section", "fields": fields})

    return blocks

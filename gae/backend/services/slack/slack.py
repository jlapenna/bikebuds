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

from shared import responses
from shared.slack_util import slack_client

from services.slack.templates import ROUTE_BLOCK


def process_slack_event(event):
    """Procesess an event.

    Args:
        event: An entity representing a full event message, including event_id, etc.
    """
    logging.debug('process_slack_event: %s', event)
    logging.debug('process_slack_event: %s', event['event']['type'])
    if event['event']['type'] == 'link_shared':
        return process_link_shared(event)
    return responses.OK_SUB_EVENT_UNKNOWN


def process_link_shared(event):
    response = slack_client.chat_unfurl(
        channel=event['event']['channel'],
        ts=event['event']['message_ts'],
        unfurls=dict((link['url'], _unfurl(link)) for link in event['event']['links']),
    )
    if not response['ok']:
        logging.error('process_link_shared: failed: %s', response)
        return responses.INTERNAL_SERVER_ERROR
    logging.debug('process_link_shared: %s', response)
    return responses.OK


def _unfurl(link):
    route = {
        'id': '',
        'created': '',
        'description': '',
        'distance': '',
        'elevation_gain': '',
        'name': '',
        'athlete.id': '',
        'athlete.firstname': '',
        'athlete.lastname': '',
        'map_image_url': 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png',
    }

    if '/routes/' in link['url']:
        return json.loads(ROUTE_BLOCK % route)

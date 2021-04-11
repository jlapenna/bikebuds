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
import re
import urllib
import urllib.request

import flask

from slack.errors import SlackApiError

from shared import responses
from shared import task_util
from shared.datastore.bot import Bot
from shared.datastore.service import Service
from shared.services.strava.client import ClientWrapper
from shared.slack_util import slack_client

from services.slack.unfurl_activity import unfurl_activity
from services.slack.unfurl_route import unfurl_route

_STRAVA_APP_LINK_REGEX = re.compile('(https://www.strava.com/([^/]+)/[0-9]+)')


module = flask.Blueprint('slack', __name__)


@module.route('/tasks/event', methods=['POST'])
def event():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('SlackEvent: %s', event.key)
    return process_slack_event(event)


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
        alt_url = _resolve_rewrite_link(link)
        unfurl = _unfurl(client, link, alt_url)
        if unfurl:
            unfurls[link['url']] = unfurl
    if not unfurls:
        return responses.OK
    logging.warning('process_link_shared: debug: unfurling: %s', unfurls)

    try:
        response = slack_client.chat_unfurl(
            channel=event['event']['channel'],
            ts=event['event']['message_ts'],
            unfurls=unfurls,
        )
    except SlackApiError as e:
        logging.exception('process_link_shared: failed: unfurling: %s', unfurls)
        logging.warning('dir: %s', dir(e))
        return responses.INTERNAL_SERVER_ERROR

    if not response['ok']:
        logging.error('process_link_shared: failed: %s with %s', response, unfurls)
        return responses.INTERNAL_SERVER_ERROR
    logging.debug('process_link_shared: %s', response)
    return responses.OK


def _resolve_rewrite_link(link):
    if 'strava.app.link' not in link['url']:
        return
    try:
        logging.info('_resolve_rewrite_link: fetching: %s', link['url'])
        with urllib.request.urlopen(link['url']) as response:
            contents = response.read()
        logging.debug('_resolve_rewrite_link: fetched: %s', link['url'])
    except urllib.request.HTTPError:
        logging.exception('Could not fetch %s', link['url'])
        return
    match = _STRAVA_APP_LINK_REGEX.search(str(contents))
    if match is None:
        logging.warning('Could not resolve %s', link['url'])
        return
    resolved_url = match.group()
    return resolved_url


def _unfurl(client, link, alt_url=None):
    url = alt_url if alt_url else link['url']
    if '/routes/' in url:
        return unfurl_route(client, url)
    elif '/activities/' in url:
        return unfurl_activity(client, url)
    else:
        return None

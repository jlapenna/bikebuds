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

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from shared import responses
from shared import task_util
from shared.datastore.bot import Bot
from shared.datastore.service import Service
from shared.services.slack.installation_store import DatastoreInstallationStore
from shared.services.strava.client import ClientWrapper

from services.slack.unfurl_activity import unfurl_activity
from services.slack.unfurl_route import unfurl_route
from shared import ds_util

_STRAVA_APP_LINK_REGEX = re.compile('(https://www.strava.com/([^/]+)/[0-9]+)')


module = flask.Blueprint('slack', __name__)


@module.route('/tasks/event', methods=['POST'])
def event():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('SlackEvent: %s', event.key)
    if event['event']['type'] == 'link_shared':
        return _process_link_shared(event)
    return responses.OK_SUB_EVENT_UNKNOWN


def _process_link_shared(event):
    slack_client = _create_slack_client(event)
    unfurls = _create_unfurls(event)
    if not unfurls:
        return responses.OK_NO_UNFURLS

    try:
        response = slack_client.chat_unfurl(
            channel=event['event']['channel'],
            ts=event['event']['message_ts'],
            unfurls=unfurls,
        )
    except SlackApiError:
        logging.exception('process_link_shared: failed: unfurling: %s', unfurls)
        return responses.INTERNAL_SERVER_ERROR

    if not response['ok']:
        logging.error('process_link_shared: failed: %s with %s', response, unfurls)
        return responses.INTERNAL_SERVER_ERROR
    logging.debug('process_link_shared: %s', response)
    return responses.OK


def _create_slack_client(event):
    slack_service = Service.get('slack', parent=Bot.key())
    installation_store = DatastoreInstallationStore(
        ds_util.client, parent=slack_service.key
    )
    slack_bot = installation_store.find_bot(
        enterprise_id=event.get('authorizations', [{}])[0].get('enterprise_id'),
        team_id=event.get('authorizations', [{}])[0].get('team_id'),
        is_enterprise_install=event.get('authorizations', [{}])[0].get(
            'is_enterprise_install'
        ),
    )
    return WebClient(slack_bot.bot_token)


def _create_unfurls(event):
    strava = Service.get('strava', parent=Bot.key())
    strava_client = ClientWrapper(strava)

    unfurls = {}
    for link in event['event']['links']:
        alt_url = _resolve_rewrite_link(link)
        unfurl = _unfurl(strava_client, link, alt_url)
        if unfurl:
            unfurls[link['url']] = unfurl
    logging.warning(f'_create_unfurls: {unfurls}')
    return unfurls


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


def _unfurl(strava_client, link, alt_url=None):
    url = alt_url if alt_url else link['url']
    if '/routes/' in url:
        return unfurl_route(strava_client, url)
    elif '/activities/' in url:
        return unfurl_activity(strava_client, url)
    else:
        return None

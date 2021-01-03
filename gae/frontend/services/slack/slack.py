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

import flask

from google.api_core.exceptions import AlreadyExists
from slackeventsapi import SlackEventAdapter

from shared import task_util
from shared.config import config
from shared.datastore.subscription import SubscriptionEvent


SERVICE_NAME = 'slack'

module = flask.Blueprint(
    SERVICE_NAME, __name__, template_folder='templates', static_folder='static'
)

slack_events_adapter = SlackEventAdapter(
    config.slack_creds['signing_secret'],
    endpoint="/services/slack/events",
    server=module,
)


@slack_events_adapter.on("link_shared")
def link_shared(event_data):
    return _handle_event(event_data)


def _handle_event(event_data):
    logging.debug('Handling Event: %s', event_data)
    event_entity = SubscriptionEvent.to_entity(
        event_data,
        name='slack-%s' % event_data['event_id'],
    )
    try:
        task_util.process_slack_event(event_entity)
    except AlreadyExists:
        logging.debug('Duplicate event: %s', event_entity.key)

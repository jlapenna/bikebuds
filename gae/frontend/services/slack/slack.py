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
from flask_cors import cross_origin

from google.api_core.exceptions import AlreadyExists
from google.cloud.datastore.entity import Entity
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import Installation
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter

from shared import auth_util
from shared import ds_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.service import Service
from shared.datastore.subscription import SubscriptionEvent
from shared.services.slack.installation_store import DatastoreInstallationStore
from shared.services.slack.state_store import DatastoreOAuthStateStore


SERVICE_NAME = 'slack'

module = flask.Blueprint(SERVICE_NAME, __name__)

slack_events_adapter = SlackEventAdapter(
    config.slack_creds['signing_secret'],
    endpoint="/events",
    server=module,
)

SCOPES = ["channels:read", "chat:write", "team:read", "links:read", "links:write"]
USER_SCOPES = ["search:read", "links:read"]

STATE_EXPIRATION_SECONDS = 60 * 5


@slack_events_adapter.on("link_shared")
def link_shared(event_data):
    logging.debug('Handling Event: %s', event_data)
    event_entity = SubscriptionEvent.to_entity(
        event_data,
        name='slack-%s' % event_data['event_id'],
    )
    try:
        task_util.slack_tasks_event(event_entity)
    except AlreadyExists:
        logging.debug('Duplicate event: %s', event_entity.key)
    return responses.OK


@module.route('/ok', methods=['GET', 'POST'])
def ok():
    return responses.OK


@module.route('/admin/init', methods=['GET', 'POST'])
@auth_util.bot_required
def admin_init(bot):
    """Step 1. Starts the service connection by redirecting to the service."""
    dest = flask.request.args.get('dest', '')
    redirect_uri = config.frontend_url + '/services/slack/admin/oauth?dest=' + dest
    return _init(bot, redirect_uri)


@module.route('/admin/oauth', methods=['GET'])
@cross_origin(origins=['https://www.slack.com'])
@auth_util.bot_required
def admin_oauth(bot):
    dest = flask.request.args.get('dest', '')
    redirect_uri = config.frontend_url + '/services/slack/admin/oauth?dest=' + dest
    return _oauth(flask.request, flask.session, bot, dest, redirect_uri)


@module.route('/init', methods=['GET', 'POST'])
@auth_util.user_required
def init(user):
    dest = flask.request.args.get('dest', '')
    redirect_uri = config.frontend_url + '/services/slack/oauth?dest=' + dest
    return _init(user, redirect_uri)


@module.route('/oauth', methods=['GET'])
@cross_origin(origins=['https://www.slack.com'])
@auth_util.user_required
def oauth(user):
    dest = flask.request.args.get('dest', '')
    redirect_uri = config.frontend_url + '/services/slack/oauth?dest=' + dest
    return _oauth(flask.request, flask.session, user, dest, redirect_uri)


def _init(user: Entity, redirect_uri: str):
    """Step 1. Starts the service connection by redirecting to the service."""
    state_store = DatastoreOAuthStateStore(ds_util.client, STATE_EXPIRATION_SECONDS)
    url_generator = AuthorizeUrlGenerator(
        client_id=config.slack_creds['client_id'],
        scopes=SCOPES,
        user_scopes=USER_SCOPES,
        redirect_uri=redirect_uri,
    )
    auth_url = url_generator.generate(state_store.issue())
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': auth_url})
    else:
        return flask.redirect(auth_url)


def _oauth(
    request: flask.Request, session: dict, user: Entity, dest: str, redirect_uri: str
):
    # Retrieve the auth code and state from the request params
    if 'code' not in request.args:
        error = request.args["error"] if "error" in request.args else ""
        return flask.make_response(
            f"Something is wrong with the installation (error: {error})", 400
        )
    code = request.args['code']

    # Verify the state parameter
    state_store = DatastoreOAuthStateStore(ds_util.client, STATE_EXPIRATION_SECONDS)
    if not state_store.consume(request.args["state"]):
        return flask.make_response(
            "Try the installation again (the state value is already expired)", 400
        )

    # Verify the state parameter
    # Complete the installation by calling oauth.v2.access API method
    client = WebClient()
    oauth_response = client.oauth_v2_access(
        client_id=config.slack_creds['client_id'],
        client_secret=config.slack_creds['client_secret'],
        redirect_uri=redirect_uri,
        code=code,
    )

    # These seem to sometimes return None rather than being unset, so for maps, return {}
    installed_enterprise = oauth_response.get("enterprise", {}) or {}
    is_enterprise_install = oauth_response.get("is_enterprise_install")
    installed_team = oauth_response.get("team", {}) or {}
    installer = oauth_response.get("authed_user", {}) or {}
    incoming_webhook = oauth_response.get("incoming_webhook", {}) or {}

    bot_token = oauth_response.get("access_token")
    # NOTE: oauth.v2.access doesn't include bot_id in response
    bot_id = None
    enterprise_url = None
    if bot_token is not None:
        auth_test = client.auth_test(token=bot_token)
        bot_id = auth_test["bot_id"]
        if is_enterprise_install is True:
            enterprise_url = auth_test.get("url")

    installation = Installation(
        app_id=oauth_response.get("app_id"),
        enterprise_id=installed_enterprise.get("id"),
        enterprise_name=installed_enterprise.get("name"),
        enterprise_url=enterprise_url,
        team_id=installed_team.get("id"),
        team_name=installed_team.get("name"),
        bot_token=bot_token,
        bot_id=bot_id,
        bot_user_id=oauth_response.get("bot_user_id"),
        bot_scopes=oauth_response.get("scope"),  # comma-separated string
        user_id=installer.get("id"),
        user_token=installer.get("access_token"),
        user_scopes=installer.get("scope"),  # comma-separated string
        incoming_webhook_url=incoming_webhook.get("url"),
        incoming_webhook_channel=incoming_webhook.get("channel"),
        incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
        incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
        is_enterprise_install=is_enterprise_install,
        token_type=oauth_response.get("token_type"),
    )

    # Store the installation
    service = Service.get(SERVICE_NAME, parent=user.key)
    store = DatastoreInstallationStore(ds_util.client, parent=service.key)
    store.save(installation)

    task_util.sync_service(Service.get(SERVICE_NAME, parent=user.key))
    return flask.redirect(config.devserver_url + dest)

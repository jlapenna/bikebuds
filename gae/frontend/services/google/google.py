# Copyright 2018 Google LLC
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

from google.cloud.datastore.entity import Entity
import google_auth_oauthlib

from shared import auth_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.service import Service


SERVICE_NAME = 'google'

module = flask.Blueprint(SERVICE_NAME, __name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
]


@module.route('/ok', methods=['GET', 'POST'])
def ok():
    return responses.OK


@module.route('/admin/init', methods=['GET', 'POST'])
@auth_util.bot_required
def admin_init(bot):
    """Step 1. Starts the service connection by redirecting to the service."""
    dest = flask.request.args.get('dest', '')
    redirect_uri = config.frontend_url + '/services/google/admin/oauth?dest=' + dest
    return _init(bot, redirect_uri)


@module.route('/admin/oauth', methods=['GET'])
@cross_origin(origins=['https://www.google.com'])
@auth_util.bot_required
def admin_oauth(bot):
    dest = flask.request.args.get('dest', '')
    redirect_uri = config.frontend_url + '/services/google/admin/oauth?dest=' + dest
    return _oauth(bot, dest, redirect_uri)


@module.route('/init', methods=['GET', 'POST'])
@auth_util.user_required
def init(user):
    dest = flask.request.args.get('dest', '')
    redirect_uri = config.frontend_url + '/services/google/oauth?dest=' + dest
    return _init(user, redirect_uri)


@module.route('/oauth', methods=['GET'])
@cross_origin(origins=['https://www.google.com'])
@auth_util.user_required
def oauth(user):
    dest = flask.request.args.get('dest', '')
    redirect_uri = config.frontend_url + '/services/google/oauth?dest=' + dest
    return _oauth(user, dest, redirect_uri)


def _init(user: Entity, redirect_uri: str):
    """Step 1. Starts the service connection by redirecting to the service."""
    Service.get(SERVICE_NAME, parent=user.key)

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config.gcp_web_creds, scopes=SCOPES
    )
    flow.redirect_uri = redirect_uri

    auth_url, flask.session['state'] = flow.authorization_url(
        access_type='offline', prompt='consent'
    )
    logging.debug('Auth state: %s', flask.session['state'])
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': auth_url})
    else:
        return flask.redirect(auth_url)


def _oauth(user: Entity, dest: str, redirect_uri: str):
    """Step 2. Stores credentials."""
    service = Service.get(SERVICE_NAME, parent=user.key)

    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config.gcp_web_creds, scopes=SCOPES, state=state
    )
    flow.redirect_uri = redirect_uri

    authorization_response = flask.request.url
    logging.debug('auth_response: %s', authorization_response)
    flow.fetch_token(authorization_response=authorization_response)
    creds = _credentials_to_dict(flow.credentials)
    logging.debug('creds: %s', creds)

    Service.update_credentials(service, creds)

    task_util.sync_service(Service.get(SERVICE_NAME, parent=user.key))
    return flask.redirect('/services/redirect?dest=' + dest)


def _credentials_to_dict(credentials) -> dict:
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }

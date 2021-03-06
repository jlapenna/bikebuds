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

import google_auth_oauthlib

from shared import auth_util
from shared import task_util
from shared.config import config
from shared.datastore.service import Service
from shared.datastore.user import User


SERVICE_NAME = 'google'

module = flask.Blueprint(SERVICE_NAME, __name__)

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.readonly',
]


@module.route('/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    """Step 1. Starts the service connection by redirecting to the service."""
    user = User.get(claims)
    Service.get(SERVICE_NAME, parent=user.key)

    dest = flask.request.args.get('dest', '')

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config.gcp_web_creds, scopes=SCOPES
    )
    flow.redirect_uri = get_redirect_uri(dest)
    auth_url, flask.session['state'] = flow.authorization_url(
        access_type='offline', include_granted_scopes='true', prompt='consent'
    )
    logging.debug('Auth state: %s', flask.session['state'])
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': auth_url})
    else:
        return flask.redirect(auth_url)


@module.route('/redirect', methods=['GET'])
@cross_origin(origins=['https://www.google.com'])
@auth_util.claims_required
def redirect(claims):
    """Step 2. Stores information coming from the service in the appropriate local store."""
    user = User.get(claims)
    service = Service.get(SERVICE_NAME, parent=user.key)

    dest = flask.request.args.get('dest', '')

    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config.gcp_web_creds, scopes=SCOPES, state=state
    )
    flow.redirect_uri = get_redirect_uri(dest)

    authorization_response = flask.request.url
    logging.debug('auth_response: %s', authorization_response)
    flow.fetch_token(authorization_response=authorization_response)
    creds = credentials_to_dict(flow.credentials)
    logging.debug('creds: %s', creds)

    Service.update_credentials(service, creds)

    task_util.sync_service(service)

    return flask.redirect('/services/redirect?dest=' + dest)


def get_redirect_uri(dest):
    """Returns a fully qualified URL for the service to redirect back to."""
    return config.frontend_url + '/services/google/redirect?dest=' + dest


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }

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

import json
import logging
import os

import flask
from flask_cors import cross_origin

import fitbit

import auth_util
from shared.config import config
from shared.datastore import services
from shared.datastore import users


SERVICE_NAME = 'fitbit'

module = flask.Blueprint(SERVICE_NAME, __name__,
        template_folder='templates',
        static_folder='static')


@module.route('/services/fitbit/test', methods=['GET', 'POST'])
@auth_util.claims_required
def test(claims):
    user = users.User.get(claims)
    service_creds = services.ServiceCredentials.default(user.key, SERVICE_NAME)
    if service_creds is None:
        return get_auth_url_response()
    service_key = services.Service.get_key(user.key, SERVICE_NAME)

    client = create_api_client(user.key, service_creds)
    logging.info('result: ' + str(client.user_profile_get()))

    return flask.make_response('OK', 200)


@module.route('/services/fitbit/sync', methods=['GET', 'POST'])
@auth_util.claims_required
def sync(claims):
    user = users.User.get(claims)
    service_creds = services.ServiceCredentials.default(user.key, SERVICE_NAME)
    if service_creds is None:
        return get_auth_url_response()
    service_key = services.Service.get_key(user.key, SERVICE_NAME)

    client = create_api_client(user.key, service_creds)
    logging.info('result: ' + str(client.user_profile_get()))

    return flask.make_response('OK', 200)


@module.route('/services/fitbit/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    user = users.User.get(claims)
    service = services.Service.get(user.key, SERVICE_NAME)

    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/services/fitbit/redirect', methods=['GET'])
@cross_origin(origins=['https://www.fitbit.com'])
@auth_util.claims_required
def redirect(claims):
    user = users.User.get(claims)
    service = services.Service.get(user.key, SERVICE_NAME)

    code = flask.request.args.get('code')
    dest = flask.request.args.get('dest', '')

    auth_client = fitbit.FitbitOauth2Client(
            client_id=config.fitbit_creds['client_id'],
            client_secret=config.fitbit_creds['client_secret'],
            redirect_uri=get_redirect_uri(dest))
    creds = auth_client.fetch_access_token(code)

    service_creds = services.ServiceCredentials.update(
            user.key, SERVICE_NAME, creds)

    return flask.redirect(config.frontend_url + dest)


def get_redirect_uri(dest):
    return config.frontend_url + '/services/fitbit/redirect?dest=' + dest


def get_auth_url_response(dest):
    auth_client = fitbit.FitbitOauth2Client(
            config.fitbit_creds['client_id'],
            config.fitbit_creds['client_secret'],
            redirect_uri=get_redirect_uri(dest))
    url, state = auth_client.authorize_token_url()
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': url})
    else:
        return flask.redirect(url)


def create_api_client(user_key, service_creds):
    def refresh_callback(new_credentials):
        services.ServiceCredentials.update(user_key, SERVICE_NAME, new_credentials)
    return fitbit.Fitbit(
            config.fitbit_creds['client_id'],
            config.fitbit_creds['client_secret'],
            access_token=service_creds.access_token,
            refresh_token=service_creds.refresh_token,
            expires_at=service_creds.expires_at,
            redirect_uri=get_redirect_uri('frontend'),
            refresh_cb=refresh_callback)

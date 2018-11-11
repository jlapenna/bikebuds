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
import flask_cors
from flask_cors import cross_origin

import firebase_admin

import stravalib

from shared.datastore import users
from shared.config import config
import auth_util
import services

SERVICE_NAME = 'strava'

module = flask.Blueprint(SERVICE_NAME, __name__,
        template_folder='templates',
        static_folder='static')


@module.route('/strava/test', methods=['GET', 'POST'])
@auth_util.claims_required
def test(claims):
    user = users.User.get(claims)
    service_creds = services.ServiceCredentials.default(user.key, SERVICE_NAME)
    if service_creds is None:
        return get_auth_url_response()

    client = stravalib.client.Client(
            access_token=service_creds.access_token)

    athlete = client.get_athlete()
    logging.info(str(athlete))
    return flask.make_response('OK', 200)


@module.route('/strava/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/strava/redirect', methods=['GET'])
@cross_origin(origins=['https://www.strava.com'])
@auth_util.claims_required
def redirect(claims):
    user = users.User.get(claims)
    service = services.Service.get(user.key, SERVICE_NAME)

    code = flask.request.args.get('code')

    client = stravalib.client.Client()
    access_token = client.exchange_code_for_token(
            client_id=config.strava_creds['client_id'],
            client_secret=config.strava_creds['client_secret'], code=code)

    services.ServiceCredentials.update(user.key, SERVICE_NAME,
            dict(access_token=access_token))

    dest = flask.request.args.get('dest', None)
    if dest:
        return flask.redirect(config.backend_url + dest)
    else:
        return flask.redirect(config.frontend_url)


def get_callback_uri(dest):
    return config.backend_url + '/' + SERVICE_NAME + '/redirect?dest=' + dest


def get_auth_url_response(dest):
    client = stravalib.client.Client()
    authorize_url = client.authorization_url(
            client_id=config.strava_creds['client_id'],
            redirect_uri=get_callback_uri(dest),
            scope='read')

    if flask.request.method == 'POST':
        return flask.jsonify({'redirect_url': authorize_url})
    else:
        return flask.redirect(authorize_url)

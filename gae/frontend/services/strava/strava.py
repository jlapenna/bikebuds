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

from google.cloud.datastore.entity import Entity

import stravalib

from shared import auth_util
from shared import ds_util
from shared import task_util
from shared.config import config
from shared.datastore.athlete import Athlete
from shared.datastore.service import Service
from shared.datastore.user import User


SERVICE_NAME = 'strava'

module = flask.Blueprint(SERVICE_NAME, __name__,
        template_folder='templates',
        static_folder='static')


@module.route('/services/strava/events', methods=['GET'])
@cross_origin(origins=['https://www.strava.com'])
def events_get():
    mode = flask.request.args.get('hub.mode')
    challenge = flask.request.args.get('hub.challenge')
    verify_token = flask.request.args.get('hub.verify_token')

    if verify_token != config.strava_creds['verify_token']:
        return 'Invalid verify_token', 401

    return flask.jsonify({'hub.challenge': challenge})


@module.route('/services/strava/events', methods=['POST'])
@cross_origin(origins=['https://www.strava.com'])
def events_post():
    # I guess someone could DOS us with events, I guess they're not
    # authenticated... These are not supplied in sub events.
    #verify_token = flask.request.args.get('hub.verify_token', None)
    #if verify_token != config.strava_creds['verify_token']:
    #    raise auth.AuthError(401, 'Invalid verify_token')

    # Events come in the form:
    #event_json = {'aspect_type': 'create',
    #        'event_time': 1549151210,
    #        'object_id': 2120237411,
    #        'object_type': 'activity',
    #        'owner_id': 35056021,
    #        'subscription_id': 133263,
    #        'updates': {}
    #        }

    event_json = None
    try:
        event_json = flask.request.get_json()
        owner_id = event_json['owner_id']

        athlete = Athlete.get_by_id(owner_id)
        if athlete is None:
            logging.warn('Received event for %s but missing Athlete', owner_id)
            return 'OK', 200

        event_entity = Entity(
                ds_util.client.key('SubscriptionEvent',
                    parent=athlete.key.parent))
        event_entity.update(event_json)
        task_util.process_event(event_entity)
    except:
        logging.exception('Failed while processing %s', event_json)
    return 'OK', 200


@module.route('/services/strava/init', methods=['GET', 'POST'])
#@cross_origin(origins=['https://www.strava.com'])
@auth_util.claims_required
def init(claims):
    user = User.get(claims)
    service = Service.get(SERVICE_NAME, parent=user.key)

    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/services/strava/redirect', methods=['GET'])
@cross_origin(origins=['https://www.strava.com'])
@auth_util.claims_required
def redirect(claims):
    user = User.get(claims)
    service = Service.get(SERVICE_NAME, parent=user.key)

    code = flask.request.args.get('code')
    dest = flask.request.args.get('dest', '')

    client = stravalib.client.Client()
    creds = client.exchange_code_for_token(
            client_id=config.strava_creds['client_id'],
            client_secret=config.strava_creds['client_secret'],
            code=code)
    creds_dict = dict(creds)

    service_creds = Service.update_credentials(service, creds_dict)

    task_util.sync_service(service)

    return flask.redirect('/services/redirect?dest=' + dest)


def get_redirect_uri(dest):
    return config.frontend_url + '/services/strava/redirect?dest=' + dest


def get_auth_url_response(dest):
    client = stravalib.client.Client()
    url = client.authorization_url(
            client_id=config.strava_creds['client_id'],
            redirect_uri=get_redirect_uri(dest),
            approval_prompt='force',
            scope=['activity:read_all', 'profile:read_all'])

    if flask.request.method == 'POST':
        return flask.jsonify({'redirect_url': url})
    else:
        return flask.redirect(url)

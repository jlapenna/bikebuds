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

import datetime
import logging

import flask
from flask_cors import cross_origin

from google.api_core.exceptions import AlreadyExists

import stravalib

from shared import auth_util
from shared import task_util
from shared.config import config
from shared.datastore.bot import Bot
from shared.datastore.athlete import Athlete
from shared.datastore.service import Service
from shared.datastore.subscription import SubscriptionEvent
from shared.datastore.user import User
from shared import responses


SERVICE_NAME = 'strava'

module = flask.Blueprint(
    SERVICE_NAME, __name__, template_folder='templates', static_folder='static'
)


@module.route('/services/strava/events', methods=['GET'])
@cross_origin(origins=['https://www.strava.com'])
def events_get():
    challenge = flask.request.args.get('hub.challenge')
    verify_token = flask.request.args.get('hub.verify_token')

    if verify_token != config.strava_creds['verify_token']:
        return responses.INVALID_TOKEN

    return flask.jsonify({'hub.challenge': challenge})


@module.route('/services/strava/events', methods=['POST'])
@cross_origin(origins=['https://www.strava.com'])
def events_post():
    # I guess someone could DOS us with events, I guess they're not
    # authenticated... These are not supplied in sub events.
    # verify_token = flask.request.args.get('hub.verify_token', None)
    # if verify_token != config.strava_creds['verify_token']:
    #    raise auth.AuthError(401, 'Invalid verify_token')

    # Events come in the form:
    # event_data = {'aspect_type': 'create',
    #        'event_time': 1549151210,
    #        'object_id': 2120237411,
    #        'object_type': 'activity',
    #        'owner_id': 35056021,
    #        'subscription_id': 133263,
    #        'updates': {}
    #        }

    event_data = None
    owner_id = None
    try:
        event_data = flask.request.get_json()
        owner_id = event_data['owner_id']
    except Exception:
        logging.exception('Failed while getting json.')

    service_key = None
    if owner_id is not None:
        athlete = Athlete.get_by_id(owner_id)
        if athlete is not None:
            service_key = athlete.key.parent
        else:
            logging.warning('Received event for %s but missing Athlete', owner_id)

    if event_data is None or service_key is None:
        sub_event_failure = SubscriptionEvent.to_entity(
            {
                'url': flask.request.url,
                'event_data': event_data,
                'failure': True,
                'date': datetime.datetime.utcnow(),
            }
        )
        logging.error('StravaEvent: failure: %s', sub_event_failure)
    else:
        event_entity = SubscriptionEvent.to_entity(event_data, parent=service_key)
        try:
            task_util.process_event(service_key, event_entity)
            logging.debug('StravaEvent: Queued: %s', event_entity.key)
        except AlreadyExists:
            logging.debug('StravaEvent: Duplicate: %s', event_entity.key)
    return responses.OK


@module.route('/services/strava/init', methods=['GET', 'POST'])
# @cross_origin(origins=['https://www.strava.com'])
@auth_util.claims_required
def init(claims):
    """Step 1. Starts the service connection by redirecting to the service."""
    # Creates the service if it doesn't exist.
    user = User.get(claims)
    Service.get(SERVICE_NAME, parent=user.key)

    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/services/strava/echo', methods=['GET'])
def echo():
    """Step 2. Echos an authentication url that can be used to store credentials."""
    url = flask.request.url.replace('echo', 'admin')
    return ECHO_RESPONSE % (url,)


@module.route('/services/strava/admin', methods=['GET'])
@cross_origin(origins=['https://www.strava.com'])
@auth_util.claims_required
def admin(claims):
    """Step 2. Stores a bot's credentials."""
    auth_util.verify_admin(flask.request)
    bot = Bot.get()
    return store_auth(bot)


@module.route('/services/strava/redirect', methods=['GET'])
@cross_origin(origins=['https://www.strava.com'])
@auth_util.claims_required
def redirect(claims):
    """Step 2. Stores information coming from the service in the appropriate local store."""
    user = User.get(claims)
    return store_auth(user)


def store_auth(user):
    service = Service.get(SERVICE_NAME, parent=user.key)

    code = flask.request.args.get('code')
    dest = flask.request.args.get('dest', '')

    client = stravalib.client.Client()
    creds = client.exchange_code_for_token(
        client_id=config.strava_creds['client_id'],
        client_secret=config.strava_creds['client_secret'],
        code=code,
    )
    creds_dict = dict(creds)

    Service.update_credentials(service, creds_dict)

    task_util.sync_service(service)

    return flask.redirect('/services/redirect?dest=' + dest)


def get_redirect_uri(dest):
    """Returns a fully qualified URL for the service to redirect back to."""
    return config.frontend_url + '/services/strava/redirect?dest=' + dest


def get_auth_url_response(dest):
    """Gets a service URL to send the user to connect."""
    client = stravalib.client.Client()
    url = client.authorization_url(
        client_id=config.strava_creds['client_id'],
        redirect_uri=get_redirect_uri(dest),
        approval_prompt='force',
        scope=['activity:read_all', 'profile:read_all'],
    )

    if flask.request.method == 'POST':
        return flask.jsonify({'redirect_url': url})
    else:
        return flask.redirect(url)


ECHO_RESPONSE = """
<html>
    <body>
        Please visit the following url from a browser logged in as a bikebuds admin:
        <br />
        <br />
        <div><strong>%s</strong></div>
    </body>
</html>
"""

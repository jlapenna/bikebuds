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

import binascii
import datetime
import logging

import flask
from flask_cors import cross_origin

from google.api_core.exceptions import AlreadyExists
from google.cloud.datastore.key import Key

from shared import auth_util
from shared import task_util
from shared.config import config
from shared.datastore.service import Service
from shared.datastore.subscription import SubscriptionEvent
from shared.datastore.user import User
from shared.services.withings.client import create_auth, create_creds_dict
from shared import responses


SERVICE_NAME = 'withings'

module = flask.Blueprint(SERVICE_NAME, __name__)


@module.route('/events', methods=['HEAD'])
@cross_origin(origins=['https://www.withings.com'])
def events_head():
    sub_secret = flask.request.args.get('sub_secret', None)
    if sub_secret != config.withings_creds['sub_secret']:
        logging.warn(
            'WithingsEvent: Invalid sub_secret: Provided %s, expected %s'
            % (sub_secret, config.withings_creds['sub_secret'])
        )
    return responses.OK


@module.route('/events', methods=['POST'])
@cross_origin(origins=['https://www.withings.com'])
def events_post():
    sub_secret = flask.request.args.get('sub_secret', None)
    if sub_secret != config.withings_creds['sub_secret']:
        logging.warn(
            'WithingsEvent: Invalid sub_secret: Provided %s, expected %s'
            % (sub_secret, config.withings_creds['sub_secret'])
        )

    # Events come POSTED in the form:
    # logging.info('Received Event: Headers:\n%s\nBody:\n%s',
    #        flask.request.headers, flask.request.get_data())
    # Headers:
    #   X-Google-Apps-Metadata: domain=gmail.com,host=*.bikebuds.cc
    #   X-Appengine-Citylatlong: 0.000000,0.000000
    #   X-Cloud-Trace-Context: \
    #       501952e8e74efe98b012acc24be99669/717376932886432083;o=1
    #   X-Appengine-Default-Namespace: gmail.com
    #   Content-Length: 63
    #   X-Appengine-Region: ?
    #   User-Agent: GuzzleHttp/6.2.1 curl/7.58.0 PHP/7.2.15-0ubuntu0.18.04.1
    #   Host: www.bikebuds.cc
    #   X-Appengine-City: ?
    #   X-Appengine-Country: FR
    #   Content-Type: application/x-www-form-urlencoded
    # Body:
    #   userid=17012450&startdate=1532017199&enddate=1532017200&appli=1
    # event_data = {
    #        'userid': 17012450,
    #        'startdate': 1532017199,
    #        'enddate': 1532017200,
    #        'appli': 1,
    #        }

    event_data = None
    try:
        event_data = flask.request.form.to_dict()
    except Exception:
        logging.error('WithingsEvent: Failed form data: %s', flask.request.form)

    service_key = None
    try:
        if 'service_key' in flask.request.args:
            service_key = Key.from_legacy_urlsafe(flask.request.args.get('service_key'))
        else:
            logging.debug(
                'WithingsEvent: service_key missing in callbackurl %s',
                flask.request.url,
            )
    except binascii.Error:
        # In older code we accidentally registered with poorly constructed
        # callbackurls, ignore these.
        logging.debug(
            'WithingsEvent: Invalid event from bad callbackurl %s', flask.request.url
        )
    except Exception:
        logging.exception(
            'WithingsEvent: Failed service_key: %s',
            flask.request.args.get('service_key'),
        )

    if event_data is None or service_key is None:
        sub_event_failure = SubscriptionEvent.to_entity(
            {
                'url': flask.request.url,
                'event_data': event_data,
                'failure': True,
                'date': datetime.datetime.utcnow(),
            },
            parent=service_key,
        )
        logging.error('WithingsEvent: failure: %s', sub_event_failure)
        return responses.OK_SUB_EVENT_FAILED

    # We can proess this entity.
    event_entity = SubscriptionEvent.to_entity(
        {
            'url': flask.request.url,
            'event_data': event_data,
            'failure': False,
            'date': datetime.datetime.utcnow(),
        },
        name=SubscriptionEvent.hash_name(*sorted(event_data.values())),
        parent=service_key,
    )
    logging.debug(
        'WithingsEvent: Processing: %s from url: %s',
        event_entity.key,
        flask.request.url,
    )
    try:
        task_util.process_event(service_key, event_entity)
        logging.info('WithingsEvent: Queued: %s', event_entity.key)
    except AlreadyExists:
        logging.info('WithingsEvent: Duplicate: %s', event_entity.key)
    return responses.OK


@module.route('/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    # Creates the service if it doesn't exist.
    user = User.get(claims)
    Service.get(SERVICE_NAME, parent=user.key)

    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/redirect', methods=['GET'])
@cross_origin(origins=['https://www.withings.com'])
@auth_util.claims_required
def redirect(claims):
    user = User.get(claims)
    service = Service.get(SERVICE_NAME, parent=user.key)

    code = flask.request.args.get('code')
    dest = flask.request.args.get('dest', '')

    auth = create_auth(callback_uri=get_callback_uri(dest))

    creds_dict = create_creds_dict(auth.get_credentials(code))
    Service.update_credentials(service, creds_dict)

    task_util.sync_service(service)

    return flask.redirect('/services/redirect?dest=' + dest)


def get_callback_uri(dest):
    return config.frontend_url + '/services/withings/redirect?dest=' + dest


def get_auth_url_response(dest):
    auth = create_auth(callback_uri=get_callback_uri(dest))
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': auth.get_authorize_url()})
    else:
        return flask.redirect(auth.get_authorize_url())

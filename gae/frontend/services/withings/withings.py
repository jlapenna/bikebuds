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

from google.appengine.ext import ndb

import flask
from flask_cors import cross_origin

import nokia 

from shared import auth_util
from shared import task_util
from shared.config import config
from shared.datastore.admin import SubscriptionEvent
from shared.datastore.services import Service
from shared.datastore.users import User


SERVICE_NAME = 'withings'

module = flask.Blueprint(SERVICE_NAME, __name__,
        template_folder='templates',
        static_folder='static')


@module.route('/services/withings/events', methods=['GET', 'HEAD', 'POST'])
@cross_origin(origins=['https://www.withings.com'])
def events_post():
    sub_secret = flask.request.args.get('sub_secret', None)
    if sub_secret != config.withings_creds['sub_secret']:
        logging.warn('Invalid sub_secret: Provided %s, expected %s'
                % (sub_secret, config.withings_creds['sub_secret']))

    # Events come POSTED in the form:
    #logging.info('Received Event: Headers:\n%s\nBody:\n%s',
    #        flask.request.headers, flask.request.get_data())
    # Headers:
    #   X-Google-Apps-Metadata: domain=gmail.com,host=*.bikebuds.cc
    #   X-Appengine-Citylatlong: 0.000000,0.000000
    #   X-Cloud-Trace-Context: 501952e8e74efe98b012acc24be99669/717376932886432083;o=1
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
    #event_data = {
    #        'userid': 17012450,
    #        'startdate': 1532017199,
    #        'enddate': 1532017200,
    #        'appli': 1,
    #        }

    service_key = ndb.Key(urlsafe=flask.request.args.get('service_key'))
    event_data = flask.request.form.to_dict()
    event_entity = SubscriptionEvent(parent=service_key, **event_data)
    task_util.process_event(event_entity)
    return 'OK', 200

def test(**kwargs):
    logging.info('kwargs: %s', kwargs)


@module.route('/services/withings/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    user = User.get(claims)
    service = Service.get(user.key, SERVICE_NAME)

    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/services/withings/redirect', methods=['GET'])
@cross_origin(origins=['https://www.withings.com'])
@auth_util.claims_required
def redirect(claims):
    user = User.get(claims)
    service = Service.get(user.key, SERVICE_NAME)

    code = flask.request.args.get('code')
    dest = flask.request.args.get('dest', '')

    auth = nokia.NokiaAuth(config.withings_creds['client_id'],
            config.withings_creds['client_secret'],
            callback_uri=get_callback_uri(dest))
    creds = auth.get_credentials(code)
    creds_dict = dict(
            access_token=creds.access_token,
            token_expiry=creds.token_expiry,
            token_type=creds.token_type,
            refresh_token=creds.refresh_token,
            user_id=creds.user_id,
            client_id=creds.client_id,
            consumer_secret=creds.consumer_secret)

    service_creds = service.update_credentials(creds_dict)

    task_util.sync_service(service)

    return flask.redirect('/services/redirect?dest=' + dest)


def get_callback_uri(dest):
    return config.frontend_url + '/services/withings/redirect?dest=' + dest


def get_auth_url_response(dest):
    auth = nokia.NokiaAuth(config.withings_creds['client_id'],
            config.withings_creds['client_secret'],
            callback_uri=get_callback_uri(dest))
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': auth.get_authorize_url()})
    else:
        return flask.redirect(auth.get_authorize_url())

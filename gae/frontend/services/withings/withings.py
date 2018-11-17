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

import auth_util
from shared.config import config
from shared.datastore import services
from shared.datastore import users
from shared.datastore.withings import Measure


SERVICE_NAME = 'withings'

module = flask.Blueprint(SERVICE_NAME, __name__,
        template_folder='templates',
        static_folder='static')


@module.route('/services/withings/test', methods=['GET', 'POST'])
@auth_util.claims_required
def test(claims):
    user = users.User.get(claims)
    service_creds = services.ServiceCredentials.default(user.key, SERVICE_NAME)
    if service_creds is None:
        return get_auth_url_response()
    client = create_api_client(user.key, service_creds)

    measures = client.get_measures(category=1)

    service_key = services.Service.get_key(user.key, SERVICE_NAME)
    query = Measure.latest_query(service_key, Measure.weight)
    results = query.fetch(1)
    return flask.make_response('OK', 200)


@module.route('/services/withings/sync', methods=['GET', 'POST'])
@auth_util.claims_required
def sync(claims):
    user = users.User.get(claims)
    service_creds = services.ServiceCredentials.default(user.key, SERVICE_NAME)
    if service_creds is None:
        return get_auth_url_response()

    lastupdate = flask.request.args.get('lastupdate', None)

    client = create_api_client(user.key, service_creds)

    service_key = services.Service.get_key(user.key, SERVICE_NAME)
    if lastupdate is None:
        latest = Measure.fetch_lastupdate(service_key)
        if len(latest) == 1:
            lastupdate = latest[0].key.id()
        else:
            lastupdate = 0

    measures = client.get_measures(lastupdate=lastupdate, category=1)

    @ndb.transactional
    def put_measures(measures, service_key):
        for measure in measures:
            Measure.to_measure(service_key, measure).put()
    put_measures(measures, service_key)
    return flask.make_response('OK', 200)


@module.route('/services/withings/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    user = users.User.get(claims)
    service = services.Service.get(user.key, SERVICE_NAME)

    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/services/withings/redirect', methods=['GET'])
@cross_origin(origins=['https://www.withings.com'])
@auth_util.claims_required
def redirect(claims):
    user = users.User.get(claims)
    service = services.Service.get(user.key, SERVICE_NAME)

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

    service_creds = services.ServiceCredentials.update(user.key, SERVICE_NAME,
        creds_dict)

    return flask.redirect(config.frontend_url + dest)


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


def create_api_client(user_key, service_creds):
    def refresh_callback(new_credentials):
        services.ServiceCredentials.update(user_key, SERVICE_NAME, new_credentials)
    return nokia.NokiaApi(service_creds, refresh_cb=refresh_callback)

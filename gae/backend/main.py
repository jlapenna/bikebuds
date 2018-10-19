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
import json
import logging
import os

from google.appengine.ext import ndb

import flask
import flask_cors
from flask_cors import cross_origin

from google.appengine.ext import ndb

import auth_util
from shared.config import config
import users
import services
from withings import withings

from strava import strava

# Firebase admin setup
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
FIREBASE_ADMIN_CREDS = credentials.Certificate(
        'lib/service_keys/bikebuds-app-firebase-adminsdk-888ix-2dfafbb556.json')
firebase_admin.initialize_app(FIREBASE_ADMIN_CREDS)

# Flask setup
app = flask.Flask(__name__)
app.register_blueprint(strava.module)
app.register_blueprint(withings.module)
flask_cors.CORS(app, origins=config.origins)


class TestModel(ndb.Expando):
    """Holds test info."""
    name = ndb.StringProperty()

    @classmethod
    def for_user(cls, claims, **kwargs):
        return TestModel(parent=ndb.Key(TestModel, claims['sub']), **kwargs)


@app.route('/test_ajax', methods=['GET'])
@auth_util.claims_required
def test_ajax(claims):
    user = users.User.get(claims)

    return flask.make_response('OK', 200)


@app.route('/test_session', methods=['GET'])
@auth_util.claims_required
def test_session():
    firebase_user = auth.get_user(claims['sub'])
    user = users.User.get(claims)

    service = services.Service.create(user, 'test_service')
    service.put()
    service_creds = services.ServiceCredentials.create(service)
    service_creds.put()
    return flask.make_response('OK', 200)


@app.route('/create_session', methods=['POST'])
@cross_origin(supports_credentials=True, origins=config.origins)
@auth_util.claims_required
def create_session(claims):
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    firebase_user = auth.get_user(claims['sub'])
    user = users.User.get(claims)

    try:
        id_token = flask.request.headers['Authorization'].split(' ').pop()
        expires_in = datetime.timedelta(days=5)
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)

        response = flask.make_response(flask.jsonify({'status': 'success'}))
        expires = datetime.datetime.now() + expires_in
        response.set_cookie('session', session_cookie, expires=expires, httponly=True)
        return response
    except auth.AuthError, e:
        logging.error(e)
        return flask.abort(401, 'Failed to create a session cookie')


@app.route('/signup', methods=['GET'])
@auth_util.claims_required
def signup(claims):
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    firebase_user = auth.get_user(claims['sub'])
    user = users.User.get(claims)

    service_names = sorted((withings.SERVICE_NAME, strava.SERVICE_NAME))
    user_services = services.Service.query(ancestor=user.key).fetch(
            len(service_names))
    user_services_dict = dict(((service.key.id(), service) for service in user_services))
    logging.info(user_services_dict)
    for service_name in service_names:
        redirect_url = config.backend_url + '/' + service_name + '/init?dest=/signup'
        if service_name not in user_services_dict:
            # We haven't initialized this service yet. Lets do it.
            return flask.redirect(redirect_url)
        service_creds = services.ServiceCredentials.default(user.key, service_name)
        if not service_creds:
            return flask.redirect(redirect_url)
        # TODO: Check if the service creds are valid.
    return flask.redirect(config.frontend_url)


@app.route('/close_session', methods=['POST'])
@cross_origin(supports_credentials=True, origins=config.origins)
def close_session():
    logging.info('/close_session')
    response = flask.make_response('OK', 200)
    response.set_cookie('session', '', expires=0)
    return response

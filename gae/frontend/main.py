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

from shared import monkeypatch

import datetime
import json
import logging
import os

import flask
import flask_cors
from flask_cors import cross_origin

from firebase_admin import auth

from shared import auth_util

from shared.config import config
from shared.datastore import services
from shared.datastore import users

from services.bbfitbit import bbfitbit as fitbit
from services.strava import strava
from services.withings import withings

# Flask setup
app = flask.Flask(__name__)
app.register_blueprint(fitbit.module)
app.register_blueprint(strava.module)
app.register_blueprint(withings.module)
flask_cors.CORS(app, origins=config.origins)


SERVICE_NAMES = (
        withings.SERVICE_NAME,
        strava.SERVICE_NAME,
        fitbit.SERVICE_NAME
        )


@app.route('/services/redirect', methods=['GET'])
def redirect():
    dest = flask.request.args.get('dest', '')
    return flask.redirect(config.devserver_url + dest)


@app.route('/services/session', methods=['POST'])
@cross_origin(supports_credentials=True, origins=config.origins)
@auth_util.claims_required
def create_session(claims):
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    user = users.User.get(claims)

    try:
        id_token = flask.request.headers['Authorization'].split(' ').pop()
        expires_in = datetime.timedelta(minutes=10)
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)

        response = flask.make_response(flask.jsonify({'status': 'success'}))
        expires = datetime.datetime.now() + expires_in
        response.set_cookie('session', session_cookie, expires=expires, httponly=True)
        logging.info(response)
        return response
    except auth.AuthError, e:
        logging.error(e)
        return flask.abort(401, 'Failed to create a session cookie')

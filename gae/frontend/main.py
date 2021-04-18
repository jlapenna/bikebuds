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
from flask_cors import CORS
from flask_cors import cross_origin
from flask_talisman import Talisman

from firebase_admin import auth, exceptions

from shared import auth_util
from shared import logging_util
from shared.config import config
from shared import responses

from services.bbfitbit import bbfitbit
from services.google import google
from services.slack import slack
from services.strava import strava
from services.withings import withings

app = flask.Flask(__name__)
app.secret_key = config.flask_secret_creds['secret']
app.register_blueprint(bbfitbit.module, url_prefix='/services/fitbit')
app.register_blueprint(google.module, url_prefix='/services/google')
app.register_blueprint(slack.module, url_prefix='/services/slack')
app.register_blueprint(strava.module, url_prefix='/services/strava')
app.register_blueprint(withings.module, url_prefix='/services/withings')
CORS(app, origins=config.cors_origins)
Talisman(app, force_https_permanent=True)

app.logger.setLevel(logging.DEBUG)
logging_util.debug_logging()
logging_util.silence_logs()


@app.route('/ok', methods=['GET', 'POST'])
def ok():
    return responses.OK


@app.route('/services/redirect', methods=['GET'])
@cross_origin(supports_credentials=True, origins=config.cors_origins)
def redirect():
    dest = flask.request.args.get('dest', '')
    return flask.redirect(config.devserver_url + dest)


@app.route('/services/session', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True, origins=config.cors_origins)
@auth_util.user_required
def create_session(user):
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    try:
        id_token = flask.request.headers['Authorization'].split(' ').pop()
        expires_in = datetime.timedelta(minutes=10)
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)

        response = flask.make_response(flask.jsonify({'status': 'success'}))
        expires = datetime.datetime.now(datetime.timezone.utc) + expires_in
        response.set_cookie(
            '__Secure-oauthsession',
            session_cookie,
            expires=expires,
            httponly=True,
            secure=True,
        )
        return response
    except exceptions.FirebaseError:
        logging.exception('Failed to create a session cookie.')
        flask.abort(401, 'Failed to create a session cookie')


@app.route('/unittest', methods=['GET', 'POST'])
def unittest():
    return responses.OK


# @app.before_request
# def before():
#     logging_util.before()
#
#
# @app.after_request
# def after(response):
#     return logging_util.after(response)


if __name__ == '__main__':
    host, port = config.frontend_url[7:].split(':')
    app.run(host='localhost', port=port, debug=True)

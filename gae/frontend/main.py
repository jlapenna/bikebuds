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

from firebase_admin import auth

from shared import auth_util
from shared import logging_util
from shared.config import config

from services.bbfitbit import bbfitbit
from services.strava import strava
from services.withings import withings

logging_util.silence_logs()

app = flask.Flask(__name__)
app.register_blueprint(bbfitbit.module)
app.register_blueprint(strava.module)
app.register_blueprint(withings.module)
CORS(app, origins=config.origins)


@app.route('/services/redirect', methods=['GET'])
@cross_origin(supports_credentials=True, origins=config.origins)
def redirect():
    dest = flask.request.args.get('dest', '')
    return flask.redirect(config.devserver_url + dest)


@app.route('/services/session', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True, origins=config.origins)
@auth_util.claims_required
def create_session(claims):
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    try:
        id_token = flask.request.headers['Authorization'].split(' ').pop()
        expires_in = datetime.timedelta(minutes=10)
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)

        response = flask.make_response(flask.jsonify({'status': 'success'}))
        expires = datetime.datetime.now(datetime.timezone.utc) + expires_in
        response.set_cookie('session', session_cookie, expires=expires, httponly=True)
        logging.info(response)
        return response
    except auth.AuthError as e:
        flask.abort(401, 'Failed to create a session cookie')


@app.before_request
def before():
    logging_util.before()


@app.after_request
def after(response):
    return logging_util.after(response)


logging_util.debug_logging()
if __name__ == '__main__':
    host, port = config.frontend_url[7:].split(':')
    app.run(host='localhost', port=port, debug=True)
else:
    # When run under dev_appserver it is not '__main__'.
    pass

import json
import logging
import os

import flask
import flask_cors
from flask_cors import cross_origin

import firebase_admin

import stravalib

from config import config
import auth_util
import services
import users

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
        return make_auth_url_response()

    client = stravalib.client.Client(
            access_token=service_creds.access_token)

    athlete = client.get_athlete()
    logging.info(str(athlete))
    return flask.make_response('OK', 200)


@module.route('/strava/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    return make_auth_url_response()


@module.route('/strava/redirect', methods=['GET'])
@cross_origin(origins=['https://www.strava.com'])
@auth_util.claims_requrired
def redirect(claims):
    user = users.User.get(claims)

    code = flask.request.args.get('code')

    client = stravalib.client.Client()
    access_token = client.exchange_code_for_token(
            client_id=config.strava_creds['client_id'],
            client_secret=config.strava_creds['client_secret'], code=code)

    services.ServiceCredentials.update(user_key, SERVICE_NAME,
            dict(access_token=access_token))

    return flask.redirect(config.frontend_url)


def make_auth_url_response():
    client = stravalib.client.Client()
    authorize_url = client.authorization_url(
            client_id=config.strava_creds['client_id'],
            redirect_uri=config.backend_url + '/strava/redirect')

    if flask.request.method == 'POST':
        return flask.jsonify({'redirect_url': authorize_url})
    else:
        return flask.redirect(authorize_url)

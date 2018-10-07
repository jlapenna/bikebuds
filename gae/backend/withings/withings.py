import json
import logging
import os

import flask
from flask_cors import cross_origin

import nokia 

import auth_util
from config import config
import users
import services


SERVICE_NAME = 'withings'

module = flask.Blueprint(SERVICE_NAME, __name__,
        template_folder='templates',
        static_folder='static')


@module.route('/withings/test', methods=['GET', 'POST'])
@auth_util.claims_required
def test(claims):
    user = users.User.get(claims)
    service_creds = services.ServiceCredentials.default(user.key, SERVICE_NAME)
    if service_creds is None:
        return get_auth_url_response()

    client = nokia.NokiaApi(service_creds)
    measures = client.get_measures(limit=1)[0]
    logging.info(measures.weight)

    return flask.make_response('OK', 200)


@module.route('/withings/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/withings/redirect', methods=['GET'])
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

    dest = flask.request.args.get('dest', None)
    if dest:
        return flask.redirect(config.backend_url + dest)
    else:
        return flask.redirect(config.frontend_url)


def get_callback_uri(dest):
    return config.backend_url + '/withings/redirect?dest=' + dest


def get_auth_url_response(dest):
    auth = nokia.NokiaAuth(config.withings_creds['client_id'],
            config.withings_creds['client_secret'],
            callback_uri=get_callback_uri(dest))
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': auth.get_authorize_url()})
    else:
        return flask.redirect(auth.get_authorize_url())

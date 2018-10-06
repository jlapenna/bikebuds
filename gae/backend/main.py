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
from config import config
import users
import services
from withings import withings

from config import config
from strava import strava

# Firebase admin setup
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
FIREBASE_ADMIN_CREDS = credentials.Certificate(
        'lib/service_keys/bikebuds-app-firebase-adminsdk-888ix-59094dc1a3.json')
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


@app.route('/close_session', methods=['POST'])
@cross_origin(supports_credentials=True, origins=config.origins)
def close_session():
    logging.info('/close_session')
    response = flask.make_response('OK', 200)
    response.set_cookie('session', '', expires=0)
    return response

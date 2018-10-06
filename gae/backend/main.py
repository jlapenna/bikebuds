import datetime
import json
import logging
import os

import flask
import flask_cors
from flask_cors import cross_origin

import auth_util
from config import config

from google.appengine.ext import ndb

# Firebase addmin setup
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
FIREBASE_ADMIN_CREDS = credentials.Certificate(
        'lib/service_keys/bikebuds-app-firebase-adminsdk-888ix-59094dc1a3.json')
firebase_admin.initialize_app(FIREBASE_ADMIN_CREDS)

# Flask setup
app = flask.Flask(__name__)
flask_cors.CORS(app, origins=config.origins)
logging.info(app.config)


class TestModel(ndb.Expando):
    """Holds test info."""
    name = ndb.StringProperty()

    @classmethod
    def for_user(cls, claims, **kwargs):
        return TestModel(parent=ndb.Key(TestModel, claims['sub']), **kwargs)


@app.route('/test_ajax', methods=['GET'])
def test_ajax():
    logging.info("/test_ajax")
    claims = auth_util.verify_claims(flask.request)
    logging.info("/test_ajax: authorized")

    test_model = TestModel.for_user(claims,
        name='datetime', value=datetime.datetime.now())
    test_model.put()
    logging.info("/test_ajax: put model")

    return flask.make_response('OK', 200)


@app.route('/test_session', methods=['GET'])
def test_session():
    session_cookie = flask.request.cookies.get('session')
    logging.info('/test_session: cookie get: ' + str(session_cookie))
    auth_util.verify_claims_from_cookie(flask.request)
    return flask.make_response('OK', 200)


@app.route('/create_session', methods=['POST'])
@cross_origin(supports_credentials=True, origins=config.origins)
def create_session():
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    auth_util.verify_claims(flask.request)

    try:
        id_token = flask.request.headers['Authorization'].split(' ').pop()
        expires_in = datetime.timedelta(days=5)
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
        response = flask.make_response(flask.jsonify({'status': 'success'}))
        expires = datetime.datetime.now() + expires_in
        response.set_cookie(
            'session', session_cookie, expires=expires, httponly=True)
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


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

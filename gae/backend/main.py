import datetime
import logging

import flask
import flask_cors
from flask_cors import cross_origin

import google.oauth2.id_token
from google.appengine.ext import ndb

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch. This needs to be ordered the way it is, for some reason.
# https://github.com/firebase/firebase-admin-python/issues/185
import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials

ORIGINS = ['http://localhost:8080', 'https://bikebuds.appspot.com']
cred = credentials.Certificate(
        'lib/service_keys/bikebuds-app-firebase-adminsdk-888ix-59094dc1a3.json')
firebase_admin.initialize_app(cred)
app = flask.Flask(__name__)
flask_cors.CORS(app, origins=ORIGINS)


class TestModel(ndb.Expando):
    """Holds test info."""
    name = ndb.StringProperty()

    @classmethod
    def for_user(cls, claims, **kwargs):
        return TestModel(parent=ndb.Key(TestModel, claims['sub']), **kwargs)


@app.route('/test_ajax', methods=['GET'])
def test_ajax():
    logging.info("/test_ajax")
    # Verify Firebase auth.
    id_token = flask.request.headers['Authorization'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(
        id_token, HTTP_REQUEST)
    if not claims:
        logging.info("/test_ajax: unauthorized")
        return 'Unauthorized', 401

    test_model = TestModel.for_user(claims,
        name='datetime', value=datetime.datetime.now())
    test_model.put()

    logging.info("/test_ajax: authorized")
    return 'OK', 200


@app.route('/test_session', methods=['GET'])
def test_session():
    session_cookie = flask.request.cookies.get('session')
    logging.info('/test_session: cookie get: ' + str(session_cookie))
    # Verify the session cookie. In this case an additional check is added to detect
    # if the user's Firebase session was revoked, user deleted/disabled, etc.
    try:
        claims = auth.verify_session_cookie(
                session_cookie, check_revoked=True)
        return flask.make_response('OK', 200)
    except ValueError, e:
        # Session cookie is unavailable or invalid. Force user to login.
        logging.info("/test_session: unauthorized: " + str(e))
        return 'Unauthorized', 401
    except auth.AuthError, e:
        # Session revoked. Force user to login.
        logging.info("/test_session: unauthorized: " + str(e))
        return 'Unauthorized', 401


@app.route('/test_cookie', methods=['GET', 'POST'])
def test_cookie():
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    response = flask.make_response(flask.jsonify({'status': 'success'}))
    response.set_cookie(
        str(datetime.datetime.now()), '', httponly=True)
    return response

@app.route('/create_session', methods=['POST'])
@cross_origin(supports_credentials=True, origins=ORIGINS)
def create_session():
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    id_token = flask.request.headers['Authorization'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(
        id_token, HTTP_REQUEST)
    if not claims:
        logging.info("/create_session: unauthorized")
        return 'Unauthorized', 401

    expires_in = datetime.timedelta(days=5)
    try:
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
@cross_origin(supports_credentials=True, origins=ORIGINS)
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

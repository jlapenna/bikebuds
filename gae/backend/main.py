import datetime
import logging
import os

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

# Firebase addmin setup
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
FIREBASE_ADMIN_CREDS = credentials.Certificate(
        'lib/service_keys/bikebuds-app-firebase-adminsdk-888ix-59094dc1a3.json')
firebase_admin.initialize_app(FIREBASE_ADMIN_CREDS)

# Environment setup
if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    BACKEND_URL = 'https://backend-dot-bikebuds-app.appspot.com'
    FRONTEND_URL = 'https://bikebuds.joelapenna.com'
else:
    BACKEND_URL = 'http://localhost:8081'
    FRONTEND_URL = 'http://localhost:8080'
ORIGINS = [BACKEND_URL, FRONTEND_URL]

# Flask setup
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
    claims = verify_claims(flask.request)
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
    verify_claims_from_cookie(flask.request)
    return flask.make_response('OK', 200)


@app.route('/create_session', methods=['POST'])
@cross_origin(supports_credentials=True, origins=ORIGINS)
def create_session():
    """From https://firebase.google.com/docs/auth/admin/manage-cookies"""
    verify_claims(flask.request)

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
@cross_origin(supports_credentials=True, origins=ORIGINS)
def close_session():
    logging.info('/close_session')
    response = flask.make_response('OK', 200)
    response.set_cookie('session', '', expires=0)
    return response


def verify_claims(request):
    """Return valid claims or throw an AuthError."""
    id_token = request.headers['Authorization'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(
        id_token, HTTP_REQUEST)
    if not claims:
        raise auth.AuthError('Unable to find valid token')
    return claims


def verify_claims_from_cookie(request):
    """Return valid claims or throw an AuthError."""
    session_cookie = request.cookies.get('session')
    # Verify the session cookie. In this case an additional check is added to
    # detect if the user's Firebase session was revoked, user deleted/disabled,
    # etc.
    try:
        return auth.verify_session_cookie( session_cookie, check_revoked=True)
    except ValueError, e:
        raise auth.AuthError('Unable to validate cookie')


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

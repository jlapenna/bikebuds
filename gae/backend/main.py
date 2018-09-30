import datetime
import logging

import flask
import flask_cors

from google.appengine.ext import ndb
import google.oauth2.id_token

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

app = flask.Flask(__name__)
flask_cors.CORS(app)


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


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

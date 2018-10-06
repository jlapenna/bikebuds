# Helper library for authentication.

import functools

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch. This needs to be ordered the way it is, for some reason.
# https://github.com/firebase/firebase-admin-python/issues/185
import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

import flask

import google.oauth2.id_token
from firebase_admin import auth


def auth_required(func):
    @functools.wraps(func)
    def wrapper():
        creds = verify(flask.request)
        return func()
    return wrapper


def verify(request):
    if request.method == 'POST':
        return verify_claims_from_header(request)
    elif request.method == 'GET':
        return verify_claims_from_cookie(request)


def verify_claims_from_header(request):
    """Return valid claims or throw an AuthError."""
    id_token = request.headers['Authorization'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(
        id_token, HTTP_REQUEST)
    if not claims:
        raise auth.AuthError(401, 'Unable to find valid token')
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
        raise auth.AuthError(401, 'Unable to validate cookie')


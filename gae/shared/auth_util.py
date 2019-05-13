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

"""Helper library for authentication."""

import functools

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch. This needs to be ordered the way it is, for some reason.
# https://github.com/firebase/firebase-admin-python/issues/185
import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

import flask
import logging

import google.oauth2.id_token
from firebase_admin import auth

from shared.datastore.users import User

def claims_required(func):
    @functools.wraps(func)
    def wrapper():
        try:
            claims = verify(flask.request)
        except auth.AuthError, e:
            return e.message, e.code
        return func(claims)
    return wrapper


def verify(request):
    if request.method == 'POST':
        return verify_claims(request)
    elif request.method == 'GET':
        return verify_claims_from_cookie(request)


def impersonate(claims, uid):
    if not uid:
        return claims
    if not User.get(claims).admin:
        raise auth.AuthError(401, 'Non-admin cannot impersonate.')
    return {'sub': uid}


def verify_claims(request, impersonate=None):
    """Return valid claims or throw an AuthError."""
    if 'Authorization' not in request.headers:
        raise auth.AuthError(401, 'Unable to find bearer in headers')
    id_token = request.headers['Authorization'].split(' ').pop()

    claims = None
    if 'UseAltAuth' in request.headers:
        # This is a standard oauth token from my python client.
        claims = google.oauth2.id_token.verify_oauth2_token(
            id_token, HTTP_REQUEST)
        # The claims have an email address that we have verified. Use that to
        # find the firebase user.
        if claims['iss'] == 'https://accounts.google.com':
            firebase_user = auth.get_user_by_email(claims['email'])
            claims = {'sub': firebase_user.uid}
    else:
        # This is a firebase token.
        claims = google.oauth2.id_token.verify_firebase_token(
            id_token, HTTP_REQUEST)

    if not claims:
        raise auth.AuthError(401, 'Unable to validate id_token')

    if not impersonate:
        return claims

    # We're impersonating someone.
    if User.get(claims).admin:
        return {'sub': impersonate}
    else:
        raise auth.AuthError(401, 'Non-admin cannot impersonate.')


def verify_claims_from_cookie(request):
    """Return valid claims or throw an AuthError."""
    session_cookie = request.cookies.get('session')
    # Verify the session cookie. In this case an additional check is added to
    # detect if the user's Firebase session was revoked, user deleted/disabled,
    # etc.
    try:
        return auth.verify_session_cookie(session_cookie, check_revoked=True)
    except ValueError, e:
        raise auth.AuthError(401, 'Unable to validate cookie')


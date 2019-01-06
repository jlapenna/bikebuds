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

import google.oauth2.id_token
from firebase_admin import auth


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
        return auth.verify_session_cookie(session_cookie, check_revoked=True)
    except ValueError, e:
        raise auth.AuthError(401, 'Unable to validate cookie')


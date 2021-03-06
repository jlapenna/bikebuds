# Copyright 2019 Google LLC
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

import flask
import logging

import google.oauth2.id_token
import google.auth.transport

from firebase_admin import auth

from shared import firebase_util
from shared.config import config


app = firebase_util.get_app()


def create_custom_token(claims):
    if config.is_dev and config.fake_user:
        logging.warn('Create Custom Token: Using Fake User')
        return b'FAKE TOKEN'
    return auth.create_custom_token(claims['sub'], app=firebase_util.get_app())


def fake_claims():
    if config.is_dev and config.fake_user:
        logging.warn('Using Fake User')
        return {
            'sub': config.fake_user,
            'roleAdmin': True,
            'roleBot': True,
            'roleUser': True,
        }
    else:
        return None


def claims_required(func):
    @functools.wraps(func)
    def wrapper():
        try:
            claims = verify(flask.request)
        except Exception as e:
            return 'Unauthorized', e.code
        return func(claims)

    return wrapper


def verify(request):
    if config.is_dev and config.fake_user:
        return fake_claims()

    # Check that there is a real user by this identity.
    claims = _verify_claims_from_headers(request)
    if not claims:
        claims = _verify_claims_from_cookie(request)
    if not claims:
        flask.abort(401, 'Unable to authenticate.')

    # Ensure we've given them access to the service.
    if not (claims.get('roleAdmin') or claims.get('roleBot') or claims.get('roleUser')):
        flask.abort(408, 'No role assigned.')
    return claims


def _verify_claims_from_headers(request, impersonate=None):
    """Return valid claims or throw an Exception."""
    if 'Authorization' not in request.headers:
        return None
    id_token = request.headers['Authorization'].split(' ').pop()

    claims = None
    firebase_user = None
    try:
        claims = google.oauth2.id_token.verify_firebase_token(
            id_token, google.auth.transport.requests.Request()
        )
        firebase_user = auth.get_user(claims['sub'])
    except ValueError:
        try:
            claims = google.oauth2.id_token.verify_oauth2_token(
                id_token, google.auth.transport.requests.Request()
            )
            # The claims have an email address that we have verified. Use that to
            # find the firebase user.
            if claims['iss'] == 'https://accounts.google.com':
                firebase_user = auth.get_user_by_email(claims['email'])
                claims = {
                    'sub': firebase_user.uid,
                    'email': claims['email'],
                    'roleAdmin': claims.get('roleAdmin', False),
                    'roleBot': claims.get('roleBot', False),
                    'roleUser': claims.get('roleUser', False),
                }
        except ValueError:
            logging.exception('Unable to verify claims')

    if not claims or not firebase_user:
        flask.abort(401, 'Unable to validate id_token')

    return claims


def _verify_claims_from_cookie(request):
    """Return valid claims or throw an Exception."""
    session_cookie = request.cookies.get('session')
    # Verify the session cookie. In this case an additional check is added to
    # detect if the user's Firebase session was revoked, user deleted/disabled,
    # etc.
    try:
        return auth.verify_session_cookie(session_cookie, check_revoked=True)
    except ValueError:
        flask.abort(401, 'Unable to validate cookie')


def verify_admin(request):
    claims = verify(flask.request)
    if not claims.get('roleAdmin'):
        flask.abort(401, 'User is not an admin')
    return claims


def get_uid_by_email(email):
    if config.is_dev and config.fake_user:
        return config.fake_user
    else:
        return auth.get_user_by_email(email).uid

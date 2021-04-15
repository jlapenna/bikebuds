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
from firebase_admin.exceptions import FirebaseError

from shared import firebase_util
from shared import responses
from shared.config import config


app = firebase_util.get_app()


def create_custom_token(claims):
    if config.is_dev and config.fake_user:
        logging.warning('Create Custom Token: Using Fake User')
        return b'FAKE TOKEN'
    return auth.create_custom_token(claims['sub'], app=firebase_util.get_app())


def admin_claims_required(func):
    @functools.wraps(func)
    def wrapper():
        return func(verify_admin(flask.request))

    return wrapper


def claims_required(func):
    @functools.wraps(func)
    def wrapper():
        return func(verify(flask.request))

    return wrapper


def verify(request: flask.Request):
    if config.is_dev and config.fake_user:
        return _fake_claims()

    # Check that there is a real user by this identity.
    claims = _verify_claims_from_headers(request)
    if not claims:
        claims = _verify_claims_from_cookie(request)
    if not claims:
        responses.abort(responses.INVALID_CLAIMS)

    # Ensure we've given them access to the service.
    if not (claims.get('roleAdmin') or claims.get('roleBot') or claims.get('roleUser')):
        responses.abort(responses.FORBIDDEN_NO_ROLE)
    return claims


def verify_admin(request: flask.Request):
    claims = verify(request)
    if not (claims and claims.get('roleAdmin')):
        responses.abort(responses.FORBIDDEN)
    return claims


def get_uid_by_email(email: str):
    if config.is_dev and config.fake_user:
        return config.fake_user
    else:
        return auth.get_user_by_email(email).uid


def _verify_claims_from_headers(request, impersonate=None):
    """Return valid claims or throw an Exception."""
    if 'Authorization' not in request.headers:
        return None
    id_token = request.headers['Authorization'].split(' ').pop()
    try:
        return google.oauth2.id_token.verify_firebase_token(
            id_token, google.auth.transport.requests.Request()
        )
    except auth.RevokedIdTokenError:
        logging.exception('firebase token has been revoked')
    except auth.ExpiredIdTokenError:
        logging.exception('firebase token is expired')
    except auth.InvalidIdTokenError:
        logging.exception('firebase token is invalid')
    return None


def _verify_claims_from_cookie(request):
    """Return valid claims or throw an Exception."""
    session_cookie = request.cookies.get('__Secure-oauthsession')
    # Verify the session cookie. In this case an additional check is added to
    # detect if the user's Firebase session was revoked, user deleted/disabled,
    # etc.
    try:
        return auth.verify_session_cookie(session_cookie, check_revoked=True)
    except FirebaseError:
        logging.exception('Session cookie was invalid')
    except ValueError:
        logging.exception('Session cookie was invalid')


def _fake_claims():
    if config.is_dev and config.fake_user:
        logging.warning('Using Fake User')
        return {
            'sub': config.fake_user,
            'roleAdmin': True,
            'roleBot': True,
            'roleUser': True,
        }
    else:
        return None

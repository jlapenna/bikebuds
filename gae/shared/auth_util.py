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
from shared.datastore.bot import Bot
from shared.datastore.user import User


logger = logging.getLogger('auth')

app = firebase_util.get_app()


def create_custom_token(request: flask.Request):
    if config.is_dev and config.fake_user:
        logger.warning('Create Custom Token: Using Fake User')
        return b'FAKE TOKEN'
    claims = _verify_claims(request)
    return auth.create_custom_token(claims['sub'], app=firebase_util.get_app())


def bot_required(func):
    @functools.wraps(func)
    def wrapper():
        return func(get_bot(flask.request))

    return wrapper


def user_required(func):
    @functools.wraps(func)
    def wrapper():
        return func(get_user(flask.request))

    return wrapper


def _verify_claims(request: flask.Request):
    if config.is_dev and config.fake_user:
        return _fake_claims()

    claims = None
    # Check that there is a real user by this identity.
    if 'Authorization' in request.headers:
        id_token = request.headers['Authorization'].split(' ').pop()
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, google.auth.transport.requests.Request()
            )
        except auth.RevokedIdTokenError:
            logger.exception('firebase token has been revoked')
            responses.abort(responses.INVALID_CLAIMS)
        except auth.ExpiredIdTokenError:
            logger.exception('firebase token is expired')
            responses.abort(responses.INVALID_CLAIMS)
        except auth.InvalidIdTokenError:
            logger.exception('firebase token is invalid')
            responses.abort(responses.INVALID_CLAIMS)

    # If no auth header provided, try to use a session cookie.
    session_cookie = request.cookies.get('__Secure-oauthsession')
    if session_cookie:
        try:
            claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        except FirebaseError:
            logger.exception('Session cookie was invalid')
            responses.abort(responses.INVALID_COOKIE)
        except ValueError:
            logger.exception('Session cookie was invalid')
            responses.abort(responses.INVALID_COOKIE)

    # Finally, also ensure we've given them access to the service.
    if not (claims.get('roleAdmin') or claims.get('roleBot') or claims.get('roleUser')):
        responses.abort(responses.FORBIDDEN_NO_ROLE)
    return claims


def get_user(request: flask.Request):
    return User.get(_verify_claims(request))


def get_admin(request: flask.Request):
    claims = _verify_claims(request)
    if 'roleAdmin' not in claims:
        responses.abort(responses.FORBIDDEN)
    return User.get(claims)


def get_bot(request: flask.Request):
    if request.headers.get('X-Appengine-Cron') == 'true':
        logger.debug('Authenticated Bot coming from X-Appengine-Cron')
        return Bot.get()

    claims = _verify_claims(request)
    if 'roleAdmin' not in claims:
        responses.abort(responses.FORBIDDEN)
    return Bot.get()


def get_uid_by_email(email: str):
    if config.is_dev and config.fake_user:
        return config.fake_user
    else:
        return auth.get_user_by_email(email).uid


def verify_gcp_claims(request: flask.Request):
    if config.is_dev and config.fake_user:
        return _fake_claims()

    id_token = request.headers['Authorization'].split(' ').pop()
    claims = google.oauth2.id_token.verify_oauth2_token(
        id_token, google.auth.transport.requests.Request()
    )
    # The claims have an email address that we have verified. Use that to
    # find the firebase user.
    if claims['iss'] == 'https://accounts.google.com':
        # TODO: verify this is actually a google server's identity, too.
        return claims
    responses.abort(responses.INVALID_CLAIMS)


def _fake_claims():
    if config.is_dev and config.fake_user:
        logger.warning('Using Fake User')
        return {
            'sub': config.fake_user,
            'roleAdmin': True,
            'roleBot': True,
            'roleUser': True,
        }
    else:
        return None

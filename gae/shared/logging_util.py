# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Helpers for better logging due to dev_appserver nonsense.

import flask
import logging
import os

from shared.config import config

LOG_HEADERS = True
LOG_QUERY = True
LOG_RESPONSE_BODY = False
LOG_RESPONSE_BODY_API = True
LOG_RESPONSE_BODY_BACKEND = True
LOG_RESPONSE_BODY_FRONTEND = True

LOGS_TO_SILENCE = [
    'DatastoreInstallationStore',
    'google.auth.transport.requests',
    'google_auth_httplib2',
    'googleapiclient.discovery',
    'slack_sdk.web.slack_response',
    'stravalib.model',
    'stravalib.model.Activity',
    'stravalib.model.Athlete',
    'stravalib.model.Club',
    'stravalib.model.BaseEntity',
    'stravalib.model.Entity',
    'stravalib.attributes.Attribute',
    'stravalib.attributes.EntityAttribute',
    'stravalib.attributes.EntityCollection',
    'urllib3.connectionpool',
    'requests_oauthlib.oauth2_session',
]

PROD_ONLY_LOGS_TO_SILENCE = [
    'bblog',
]


def _set_logging_config(logger):
    base = '[%(levelname).1s:%(name)s:%(filename)s:%(lineno)s] %(message)s'
    if config.is_dev:
        # Include log time in dev.
        logger.basicConfig(
            format='%(asctime)s [' + os.environ.get('GAE_SERVICE', '') + ']' + base
        )
    else:
        # But don't include it in prod, gcp logging includes a timestamp.
        logger.basicConfig(format=base)


_set_logging_config(logging)

request_logger = logging.getLogger('bblog.request')
response_logger = logging.getLogger('bblog.response')


def _debug_logging(app=None):
    # dev_appserver doesn't seem to properly set up logging.
    if app:
        app.logger.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)


def setup_logging(app=None):
    _debug_logging(app)
    _silence_logs(app)


# From: https://stackoverflow.com/a/39734260
# Useful debugging interceptor to log all values posted to the endpoint
def before():
    query = 'query: '
    headers = 'headers: '
    if not LOG_QUERY:
        query += '(skipped)'
    elif len(flask.request.values) == 0:
        query += '(None)'
    else:
        query += ', '.join(['%s=%s' % (k, v) for k, v in flask.request.values.items()])
    if not LOG_HEADERS:
        headers += '(skipped)'
    else:
        headers += ', '.join(
            ['%s=%s' % (k, v) for k, v in flask.request.headers.items()]
        )
    request_logger.debug(
        '%s %s: %s; %s', flask.request.method, flask.request.path, query, headers
    )


# Useful debugging interceptor to log all endpoint responses
def after(response):
    try:
        if not LOG_RESPONSE_BODY:
            body = ''
        elif flask.request.path.endswith('png'):
            body = 'png'
        elif flask.request.host_url == config.api_url:
            if LOG_RESPONSE_BODY_API:
                body = len(response.data.decode('utf-8'))
            else:
                body = 'api response'
        elif flask.request.host_url == config.backend_url:
            if LOG_RESPONSE_BODY_BACKEND:
                body = response.data.decode('utf-8')
            else:
                body = 'backend response'
        elif flask.request.host_url == config.frontend_url:
            if LOG_RESPONSE_BODY_FRONTEND:
                body = response.data.decode('utf-8')
            else:
                body = 'frontend response'
        response_logger.debug(
            '%s %s: response: %s, %s',
            flask.request.method,
            flask.request.path,
            response.status,
            body,
        )
    except Exception:
        response_logger.debug(
            '%s %s: response: could not parse', flask.request.method, flask.request.path
        )
    return response


def _silence_logs(app=None):
    for log in LOGS_TO_SILENCE:
        logging.getLogger(log).setLevel(logging.ERROR)
    if not config.is_dev:
        for log in PROD_ONLY_LOGS_TO_SILENCE:
            logging.getLogger(log).setLevel(logging.ERROR)

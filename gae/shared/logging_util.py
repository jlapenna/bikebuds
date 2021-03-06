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

from shared.config import config


# Alias our logger for later hacks.
bb_logger = logging.getLogger()

LOG_HEADERS = False
LOG_QUERY = False
LOG_RESPONSES = False

LOGS_TO_SILENCE = [
    'urllib3.connectionpool',
    # 'oauth2client.contrib.multistore_file',
    # 'requests_oauthlib.oauth2_session',
    'stravalib.model.Activity',
    'stravalib.model.Athlete',
    'stravalib.model.Club',
    'stravalib.attributes.EntityCollection',
    # 'google.auth.transport.requests',
    # 'google_auth_httplib2',
    # 'garminconnect',
]

PROD_ONLY_LOGS_TO_SILENCE = []


def all_logging():
    # Standardize default logging.
    logging.basicConfig(
        format='%(levelname)s\t %(asctime)s %(filename)s:%(lineno)s]\t%(message)s'  # noqa: E501
    )


def debug_logging():
    all_logging()

    # dev_appserver doesn't seem to properly set up logging.
    bb_logger.setLevel(logging.DEBUG)

    # From:
    #     https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f
    # gunicorn_logger = logging.getLogger('gunicorn.error')
    # gunicorn_logger.setLevel(logging.DEBUG)
    # werkzeug_logger = logging.getLogger('werkzeug')
    # werkzeug_logger.setLevel(logging.DEBUG)


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
    bb_logger.debug(
        '%s %s: %s; %s', flask.request.method, flask.request.path, query, headers
    )


# Useful debugging interceptor to log all endpoint responses
def after(response):
    if not LOG_RESPONSES:
        body = ''
    elif flask.request.path in ['/activities', '/swagger.json', '/series']:
        body = len(response.data.decode('utf-8'))
    else:
        body = response.data.decode('utf-8')
    try:
        bb_logger.debug(
            '%s %s: response: %s, %s',
            flask.request.method,
            flask.request.path,
            response.status,
            body,
        )
    except Exception:
        bb_logger.debug(
            '%s %s: response: could not parse', flask.request.method, flask.request.path
        )
    return response


def silence_logs():
    for log in LOGS_TO_SILENCE:
        logging.getLogger(log).setLevel(logging.ERROR)
    if not config.is_dev:
        for log in PROD_ONLY_LOGS_TO_SILENCE:
            logging.getLogger(log).setLevel(logging.ERROR)

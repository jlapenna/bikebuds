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


# Alias our logger for later hacks.
bb_logger = logging.getLogger()


def all_logging():
    # Standardize default logging.
    logging.basicConfig(
            format='%(levelname)s\t %(asctime)s %(filename)s:%(lineno)s] %(message)s')

def debug_logging():
    all_logging()

    # dev_appserver doesn't seem to properly set up logging.
    bb_logger.setLevel(logging.DEBUG)

    # From: https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f
    #gunicorn_logger = logging.getLogger('gunicorn.error')
    #gunicorn_logger.setLevel(logging.DEBUG)
    #werkzeug_logger = logging.getLogger('werkzeug')
    #werkzeug_logger.setLevel(logging.DEBUG)


# From: https://stackoverflow.com/a/39734260
# Useful debugging interceptor to log all values posted to the endpoint
def before():
    query = 'query: '
    headers = 'headers: '
    if len(flask.request.values) == 0:
        query += '(None)'
    query += ', '.join(['%s=%s' % (k, v) for k,v in flask.request.values.items()])
    headers += ', '.join(['%s=%s' % (k, v) for k,v in flask.request.headers.items()])
    bb_logger.debug('%s %s: %s; %s', flask.request.method, flask.request.path, query, headers)

# Useful debugging interceptor to log all endpoint responses
def after(response):
    try:
        bb_logger.debug('%s: response: %s, %s', flask.request.path,
                response.status, response.data.decode('utf-8'))
    except:
        bb_logger.debug('%s: response: could not parse', flask.request.path)
    return response


def silence_logs():
    logging.getLogger('oauth2client.contrib.multistore_file').setLevel(logging.ERROR)
    logging.getLogger('stravalib.model.Activity').setLevel(logging.WARN)
    logging.getLogger('stravalib.model.Athlete').setLevel(logging.WARN)
    logging.getLogger('stravalib.model.Club').setLevel(logging.WARN)

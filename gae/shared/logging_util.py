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

def debug_logging():
    # dev_appserver doesn't seem to properly set up logging.
    logging.getLogger().setLevel(logging.DEBUG)

    # From: https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f
    gunicorn_logger = logging.getLogger('gunicorn.error')
    gunicorn_logger.setLevel(logging.DEBUG)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.DEBUG)


# From: https://stackoverflow.com/a/39734260
# Useful warnging interceptor to log all values posted to the endpoint
def before():
    query = 'query: '
    headers = 'headers: '
    if len(flask.request.values) == 0:
        query += '(None)'
    for key in flask.request.values:
        query += '%s:%s, ' % (key, flask.request.values[key])
    for k, v in flask.request.headers.items():
        headers += '%s:%s, ' % (k, v)
    logging.warn('%s; %s', query, headers)

# Useful warnging interceptor to log all endpoint responses
def after(response):
    try:
        logging.warn('response: %s, %s', response.status, response.data.decode('utf-8'))
    except:
        logging.warn('response: could not parse')
    return response

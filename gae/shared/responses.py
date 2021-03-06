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

import collections

import flask


class ResponseException(Exception):
    def __init__(self, response):
        self.code = response.code
        self.description = response.message


def abort(response):
    flask.abort(response.code, response.message)


Response = collections.namedtuple('Response', ('message', 'code'))

OK = Response('OK', 200)
# 200, because this is what withings requires as a response.
OK_SUB_EVENT_FAILED = Response('SUB_EVENT_FAILED', 200)

OK_SYNC_EXCEPTION = Response('UNKNOWN EXCEPTION', 201)
OK_NO_SERVICE = Response('NO SERVICE', 210)
OK_NO_CREDENTIALS = Response('NO CREDENTIALS', 220)
OK_INVALID_STATE_KEY = Response('INVALID STATE_KEY', 230)
OK_SUB_EVENT_UNKNOWN = Response('SUB_EVENT_UNKNOWN', 240)
OK_INVALID_LIVETRACK = Response('INVALID LIVETRACK', 250)
OK_UNKNOWN_EXCEPTION = Response('UNKNOWN EXCEPTION', 299)

BAD_REQUEST = Response('BAD REQUEST', 400)
NO_AUTH_HEADER = Response('BAD REQUEST: Unable to find bearer in headers', 400)
INVALID_TOKEN = Response('INVALID VERIFY_TOKEN', 401)

INTERNAL_SERVER_ERROR = Response('INTERNAL SERVER ERROR', 500)

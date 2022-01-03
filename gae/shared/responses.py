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

from werkzeug.wrappers.response import Response as WResponse


Response = collections.namedtuple('Response', ('message', 'code'))

OK = Response('OK', 200)
# 200, because this is what withings requires as a response.
OK_SUB_EVENT_FAILED = Response('SUB_EVENT_FAILED', 200)
OK_NO_UNFURLS = Response('NO_UNFURLS', 200)

OK_SYNC_EXCEPTION = Response('UNKNOWN EXCEPTION', 201)
OK_NO_SERVICE = Response('NO SERVICE', 210)
OK_NO_CREDENTIALS = Response('NO CREDENTIALS', 220)
OK_INVALID_STATE_KEY = Response('INVALID STATE_KEY', 230)
OK_SUB_EVENT_UNKNOWN = Response('SUB_EVENT_UNKNOWN', 240)
OK_INVALID_LIVETRACK = Response('INVALID LIVETRACK', 250)
OK_UNKNOWN_EXCEPTION = Response('UNKNOWN EXCEPTION', 299)

BAD_REQUEST = Response('BAD REQUEST', 400)
INVALID_TOKEN = Response('INVALID VERIFY_TOKEN', 401)
INVALID_COOKIE = Response('INVALID COOKIE', 401)
INVALID_CLAIMS = Response('INVALID CLAIMS', 401)
FORBIDDEN = Response('FORBIDDEN', 403)
FORBIDDEN_NO_ROLE = Response('FORBIDDEN_NO_ROLE', 403)

INTERNAL_SERVER_ERROR = Response('INTERNAL SERVER ERROR', 500)


def abort(response: Response):
    flask.abort(response.code, response.message)


def assertResponse(test_case, first, second):
    if isinstance(second, WResponse):
        if second.content_type == 'application/json':
            test_case.assertTupleEqual(first, (second.json, second.status_code))
        else:
            test_case.assertTupleEqual(
                first, (second.data.decode('utf-8'), second.status_code)
            )
    else:
        test_case.assertEqual(first, second)
        # msg=f'Got "{r.status}" but expected {expected}')

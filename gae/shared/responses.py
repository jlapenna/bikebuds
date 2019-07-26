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


Response = collections.namedtuple('Response', ('message', 'code'))


class Responses(object):
    OK = Response('OK', 200)
    OK_SYNC_EXCEPTION = Response('UNKNOWN EXCEPTION', 201)
    OK_NO_SERVICE = Response('NO SERVICE', 210)
    OK_NO_CREDENTIALS = Response('NO CREDENTIALS', 220)
    OK_INVALID_STATE_KEY = Response('INVALID STATE_KEY', 230)

    OK_UNKNOWN_EXCEPTION = Response('UNKNOWN EXCEPTION', 299)
    BAD_REQUEST = Response('BAD REQUEST', 400)
    INVALID_TOKEN = Response('INVALID VERIFY_TOKEN', 401)

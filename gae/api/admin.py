# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import flask

from flask_restplus import Resource, Namespace

from shared import auth_util
from shared.datastore.user import User

api = Namespace('admin', 'Bikebuds Admin API')


@api.route('/test')
class TestResource(Resource):
    def get(self):
        claims = auth_util.verify_admin(flask.request)
        return {}

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
from shared import ds_util
from shared import task_util

api = Namespace('admin', 'Bikebuds Admin API')


@api.route('/process_events')
class ProcessEventsResource(Resource):
    def get(self):
        auth_util.verify_admin(flask.request)

        sub_events_query = ds_util.client.query(kind='SubscriptionEvent')
        for sub_event in sub_events_query.fetch():
            task_util.process_event(sub_event.key)

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

import logging

import flask

from flask_restplus import Resource, Namespace

from shared import auth_util
from shared import ds_util
from shared import task_util
from shared.responses import Responses
from shared.services.withings.client import create_client as withings_create_client

api = Namespace('admin', 'Bikebuds Admin API')


@api.route('/process_events')
class ProcessEventsResource(Resource):
    def get(self):
        auth_util.verify_admin(flask.request)

        sub_events_query = ds_util.client.query(kind='SubscriptionEvent')
        for sub_event in sub_events_query.fetch():
            task_util.process_event(sub_event.key)
        return Responses.OK


@api.route('/subscription/remove')
class RemoveSubscriptionResource(Resource):
    @api.doc('remove_subscription')
    def post(self):
        auth_util.verify_admin(flask.request)

        callbackurl = flask.request.form.get('callbackurl', None)
        logging.info('Unsubscribing: %s', callbackurl)

        if callbackurl is None or 'withings' not in callbackurl:
            return Responses.BAD_REQUEST

        services_query = ds_util.client.query(kind='Service')
        services_query.add_filter('sync_enabled', '=', True)
        services = [
            service
            for service in services_query.fetch()
            if service.key.name == 'withings' and service.get('credentials') is not None
        ]

        for service in services:
            logging.info('Unsubscribing: %s from %s', callbackurl, service.key)
            client = withings_create_client(service)
            results = []
            try:
                result = client.unsubscribe(callbackurl)
                logging.info(
                    'Unsubscribed %s from %s (%s)', callbackurl, service.key, result
                )
                results.append(
                    {
                        'callbackurl': callbackurl,
                        'result': str(result),
                        'service': str(service.key),
                    }
                )
            except Exception as e:
                logging.exception(
                    'Unable to unsubscribe %s from %s', callbackurl, service.key
                )
                results.append(
                    {
                        'callbackurl': callbackurl,
                        'error': str(e),
                        'service': str(service.key),
                    }
                )
        return results

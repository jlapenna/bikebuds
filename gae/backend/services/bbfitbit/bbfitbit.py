# Copyright 2018 Google LLC
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

import logging

import fitbit
import flask

from shared import ds_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.series import Series
from shared.datastore.service import Service
from shared.exceptions import SyncException

import sync_helper


module = flask.Blueprint('fitbit', __name__)


@module.route('/tasks/sync', methods=['POST'])
def sync():
    logging.debug('Syncing: bbfitbit')
    params = task_util.get_payload(flask.request)

    service = ds_util.client.get(params['service_key'])
    if not Service.has_credentials(service):
        logging.warning('No creds: %s', service.key)
        Service.set_sync_finished(service, error='No credentials')
        return responses.OK_NO_CREDENTIALS

    try:
        Service.set_sync_started(service)
        sync_helper.do(Worker(service), work_key=service.key)
        Service.set_sync_finished(service)
        return responses.OK
    except SyncException as e:
        Service.set_sync_finished(service, error=str(e))
        return responses.OK_SYNC_EXCEPTION


class Worker(object):
    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        measures = self.client.time_series('body/weight', period='max')

        series = Series.to_entity(measures['body-weight'], parent=self.service.key)
        ds_util.client.put(series)


def create_client(service):
    if not Service.has_credentials(service):
        raise Exception('Cannot create Fitbit client without creds: %s', service)

    def refresh_callback(new_credentials):
        logging.debug('Fitbit creds refresh for: %s', service.key)
        Service.update_credentials(service, new_credentials)

    return fitbit.Fitbit(
        config.fitbit_creds['client_id'],
        config.fitbit_creds['client_secret'],
        access_token=service['credentials']['access_token'],
        refresh_token=service['credentials']['refresh_token'],
        expires_at=service['credentials']['expires_at'],
        redirect_uri=get_redirect_uri('frontend'),
        refresh_cb=refresh_callback,
        system=fitbit.Fitbit.METRIC,
    )


def get_redirect_uri(dest):
    return config.frontend_url + '/services/fitbit/redirect?dest=' + dest

# Copyright 2021 Google LLC
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

import flask

from shared import ds_util
from shared import responses
from shared import task_util
from shared.datastore.service import Service
from shared.exceptions import SyncException
from shared.services.trainerroad.client import create_client

import sync_helper


module = flask.Blueprint('trainerroad', __name__)


@module.route('/tasks/sync', methods=['POST'])
def sync():
    logging.debug('Syncing: trainerroad')
    params = task_util.get_payload(flask.request)

    service = ds_util.client.get(params['service_key'])
    if not Service.has_credentials(service, required_key='password'):
        logging.warn('No creds: %s', service.key)
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
        with self.client:
            logging.debug('Getting FTP')
            ftp = self.client.ftp
            logging.debug('Fetched FTP: %s', ftp)

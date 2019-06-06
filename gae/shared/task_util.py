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

"""Helpers for the cloud tasks queue."""

import datetime
import os
import logging

import requests

from google.cloud import tasks_v2
from google.cloud.datastore import helpers
from google.cloud.datastore.entity import Entity
from google.cloud.datastore_v1.proto import entity_pb2
from google.oauth2.service_account import Credentials

from shared import ds_util
from shared.config import config
from shared.datastore.service import Service

if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    # Production
    credentials = None
else:
    # Local
    credentials = Credentials.from_service_account_file(
            'env/service_keys/python-client-testing.json')

# Create a client.
_client = tasks_v2.CloudTasksClient(credentials=credentials)
_parent = _client.queue_path(config.project_id, config.tasks_location, 'default')


def _serialize_entity(entity):
    """Converts an Entity object to a serialized proto string."""
    if entity is None:
        return None
    return helpers.entity_to_protobuf(entity).SerializeToString()


def _deserialize_entity(pb_bytes):
    """Converts a serialized proto string to an Entity object."""
    if pb_bytes is None:
        return None
    entity = entity_pb2.Entity()
    entity.ParseFromString(pb_bytes)
    return helpers.entity_from_protobuf(entity)


def _queue_task(entity=None, relative_uri=None, service='default'):
    task = {
        'app_engine_http_request': {
            'http_method': 'POST',
            'relative_uri': relative_uri,
            'app_engine_routing': {'service': service}
        }
    }

    converted_payload = None
    if entity is not None:
        # The API expects a payload of type bytes.
        converted_payload = _serialize_entity(entity)

        # Add the payload to the request.
        task['app_engine_http_request']['body'] = converted_payload
    logging.info('Queueing task: %s', task)

    if config.is_dev:
        # Override when running locally.
        if service == 'default':
            service == 'frontend'
        url = getattr(config, service + '_url') + relative_uri
        response = requests.post(url, data=converted_payload)
        logging.info('Queued task: response: %s', response)
        return response

    return _client.create_task(_parent, task)


def sync_service(service):
    sync_services([service])


def sync_services(services):
    # We have to do this "do" nonsense, because when on dev we fake tasks by
    # just triggering them via http, and the transaction hasn't written the
    # values yet, so the other server can't read them if they get processed
    # before the transaction completes.
    def do():
        state = Entity(ds_util.client.key('SyncState', datetime.datetime.utcnow().isoformat()))
        state['completed_tasks'] = 0
        ds_util.client.put(state)

        tasks = []
        for service in services:
            user_key = service.key.parent
            service['sync_date'] = datetime.datetime.now()
            service['syncing'] = True

            tasks.append({
                'relative_uri': '/tasks/service_sync/' + service.key.name,
                'service': 'backend',
                'entity': params_entity(state_key=state.key, service_key=service.key)
                })
            logging.warn('Added: %s', tasks[-1])

        # Write the number of tasks we're about to queue.
        state['total_tasks'] = len(tasks)
        ds_util.client.put(state)
        logging.warn('Put state: %s', state)

        # Queue all the tasks.
        for task in tasks:
            _queue_task(**task)
    if not config.is_dev:
        with ds_util.client.transaction():
            do()
    else:
        do()


def get_payload(request):
    return _deserialize_entity(request.get_data())


def maybe_finish_sync_services_and_queue_process(service, state_key):
    # We have to do this "do" nonsense, because when on dev we fake tasks by
    # just triggering them via http, and the transaction hasn't written the
    # values yet, so the other server can't read them if they get processed
    # before the transaction completes.
    def do():
        logging.warn('Incrementing completed tasks for %s', state_key)
        state = ds_util.client.get(state_key)
        logging.warn('Fetched %s and it is %s', state_key, state)
        state['completed_tasks'] += 1
        ds_util.client.put(state)

        service['syncing'] = False
        service['sync_successful'] = True
        ds_util.client.put(service)

        if state['completed_tasks'] == state['total_tasks']:
            logging.info('Completed all pending tasks for %s', state.key)
            _queue_task(**{
                'relative_uri': '/tasks/process',
                'service': 'backend',
                'entity': params_entity(state_key=state.key)
                })
    if not config.is_dev:
        with ds_util.client.transaction():
            do()
    else:
        do()


def params_entity(**kwargs):
    params_entity = Entity(ds_util.client.key('TaskParams'))
    params_entity.update(**kwargs)
    return params_entity


def test(entity=None):
    return _queue_task(entity=entity, relative_uri='/tasks/test', service='backend')

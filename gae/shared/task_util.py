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
import logging

import requests

from google.cloud import tasks_v2
from google.cloud.datastore import helpers
from google.cloud.datastore.entity import Entity
from google.cloud.datastore_v1.proto import entity_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from shared import ds_util
from shared.config import config
from shared.credentials import credentials
from shared.datastore.service import Service


# Create a client.
_client = tasks_v2.CloudTasksClient(credentials=credentials)

_default_parent = _client.queue_path(
    config.project_id, config.tasks_location, 'default'
)
_events_parent = _client.queue_path(config.project_id, config.tasks_location, 'events')
_notifications_parent = _client.queue_path(
    config.project_id, config.tasks_location, 'notifications'
)


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


def _queue_task(
    name=None,
    parent=None,
    entity=None,
    relative_uri=None,
    service='default',
    delay_timedelta=None,
):
    task = {
        'app_engine_http_request': {
            'http_method': 'POST',
            'relative_uri': relative_uri,
            'app_engine_routing': {'service': service},
        }
    }

    if parent is None:
        parent = _default_parent

    if name is not None:
        task['name'] = '%s/tasks/%s' % (parent, name)

    if delay_timedelta:
        future_time = datetime.datetime.utcnow() + delay_timedelta
        timestamp = Timestamp()
        timestamp.FromDatetime(future_time)
        task['schedule_time'] = timestamp

    converted_payload = None
    if entity is not None:
        # The API expects a payload of type bytes.
        converted_payload = _serialize_entity(entity)

        # Add the payload to the request.
        task['app_engine_http_request']['body'] = converted_payload

    logging.debug('Queueing task: %s', task['app_engine_http_request']['relative_uri'])
    if config.is_dev:
        # Override when running locally.
        if service == 'default':
            service == 'frontend'
        url = getattr(config, service + '_url') + relative_uri
        response = requests.post(url, data=converted_payload)
        logging.info(
            'Queued task: %s response: %s',
            task['app_engine_http_request']['relative_uri'],
            response,
        )
        return response

    return _client.create_task(parent, task)


def _params_entity(**kwargs):
    params_entity = Entity(ds_util.client.key('TaskParams'))
    params_entity.update(**kwargs)
    return params_entity


def sync_club(club_id):
    return _queue_task(
        **{'relative_uri': '/tasks/sync/club/%s' % club_id, 'service': 'backend'}
    )


def sync_service(service):
    sync_services([service])


def sync_services(services):
    # We have to do this "do" nonsense, because when on dev we fake tasks by
    # just triggering them via http, and the transaction hasn't written the
    # values yet, so the other server can't read them if they get processed
    # before the transaction completes.
    def do():
        state = Entity(
            ds_util.client.key(
                'SyncState', datetime.datetime.now(datetime.timezone.utc).isoformat()
            )
        )
        state['completed_tasks'] = 0
        ds_util.client.put(state)

        tasks = []
        for service in services:
            if service['sync_state'].get('syncing'):
                logging.debug(
                    'Not enqueuing sync for %s; already started.', service.key
                )
                continue
            Service.set_sync_enqueued(service)
            tasks.append(
                {
                    'entity': _params_entity(
                        state_key=state.key, service_key=service.key
                    ),
                    'relative_uri': '/tasks/sync/service/' + service.key.name,
                    'service': 'backend',
                }
            )
            logging.debug('Added: %s', tasks[-1])

        # Write the number of tasks we're about to queue.
        state['total_tasks'] = len(tasks)
        ds_util.client.put(state)

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


def maybe_finish_sync_services(state_key=None):
    if not state_key:
        logging.warn('Cannot Increment completed tasks')
        return

    # We have to do this "do" nonsense, because when on dev we fake tasks by
    # just triggering them via http, and the transaction hasn't written the
    # values yet, so the other server can't read them if they get processed
    # before the transaction completes.
    def do():
        logging.debug('Incrementing completed tasks for %s', state_key)
        state = ds_util.client.get(state_key)
        state['completed_tasks'] += 1
        ds_util.client.put(state)

        if state['completed_tasks'] == state['total_tasks']:
            logging.debug('Completed all pending tasks for %s', state.key)
            # _queue_task(**{
            #    'entity': _params_entity(state_key=state.key),
            #    'relative_uri': '/tasks/process',
            #    'service': 'backend',
            #    })

    if not config.is_dev:
        with ds_util.client.transaction():
            do()
    else:
        do()


def process_event(event_key):
    return _queue_task(
        name=event_key.name,
        entity=_params_entity(event_key=event_key),
        relative_uri='/tasks/process_event',
        service='backend',
        parent=_events_parent,
        delay_timedelta=datetime.timedelta(seconds=5),
    )


def process_weight_trend(service):
    return _queue_task(
        entity=_params_entity(service_key=service.key),
        relative_uri='/tasks/process_weight_trend',
        service='backend',
        parent=_notifications_parent,
    )


def task_body_for_test(**kwargs):
    params_entity = _params_entity(**kwargs)
    return _serialize_entity(params_entity)

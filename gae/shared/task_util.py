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
from google.cloud.datastore.key import Key
from google.cloud.datastore_v1.types import entity as entity_pb2

# from google.cloud.datastore_v1.proto import entity_pb2
# from google.cloud.proto.datastore.v1 import entity_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from shared import ds_util
from shared.config import config
from shared.datastore.service import Service


# Create a client.
_client = tasks_v2.CloudTasksClient()


# REMINDER: Don't forget to update queues.sh!
_default_parent = _client.queue_path(
    config.project_id, config.tasks_location, 'default'
)
_events_parent = _client.queue_path(config.project_id, config.tasks_location, 'events')
_slack_events_parent = _client.queue_path(
    config.project_id, config.tasks_location, 'slack'
)
_notifications_parent = _client.queue_path(
    config.project_id, config.tasks_location, 'notifications'
)
_backfill_parent = _client.queue_path(
    config.project_id, config.tasks_location, 'backfill'
)
_gmail_parent = _client.queue_path(config.project_id, config.tasks_location, 'gmail')
_livetrack_parent = _client.queue_path(
    config.project_id, config.tasks_location, 'livetrack'
)


def _serialize_entity(entity):
    """Converts an Entity object to a serialized proto string."""
    if entity is None:
        return None
    return helpers.entity_to_protobuf(entity)._pb.SerializeToString()


def _deserialize_entity(pb_bytes):
    """Converts a serialized proto string to an Entity object."""
    if pb_bytes is None:
        return None
    entity = entity_pb2.Entity()
    entity._pb.ParseFromString(pb_bytes)
    return helpers.entity_from_protobuf(entity._pb)


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

    if config.is_dev:
        logging.debug(
            'Executing task for dev: %s',
            task['app_engine_http_request']['relative_uri'],
        )
        return _post_task_for_dev(task, service, relative_uri, converted_payload)
    else:
        logging.debug(
            'Queueing task: %s', task['app_engine_http_request']['relative_uri']
        )
        return _client.create_task(request={'parent': parent, 'task': task})


def _post_task_for_dev(task, service, relative_uri, converted_payload):
    if service == 'default':
        # Override when running locally.
        service == 'frontend'
    url = getattr(config, service + '_url') + relative_uri
    response = requests.post(url, data=converted_payload)
    logging.info(
        'Executed task: %s response: %s',
        task['app_engine_http_request']['relative_uri'],
        response,
    )
    return response


def _params_entity(**kwargs):
    params_entity = Entity(ds_util.client.key('TaskParams'))
    params_entity.update(**kwargs)
    return params_entity


def sync_club(club_id):
    return _queue_task(
        **{
            'relative_uri': '/services/strava/tasks/sync/club/%s' % club_id,
            'service': 'backend',
        }
    )


def sync_service(service, force=False):
    sync_services([service], force=force)


def sync_services(services, force=False):
    def do():
        for service in services:
            if service['sync_state'].get('syncing') and force:
                logging.debug('Forcing sync finished: %s', service.key)
                Service.set_sync_finished(service, error='Forced sync')

            if service['sync_state'].get('syncing'):
                logging.debug(
                    'Not enqueuing sync for %s; already started.', service.key
                )
                continue
            Service.set_sync_enqueued(service)
            task = {
                'entity': _params_entity(service_key=service.key),
                'relative_uri': '/services/%s/tasks/sync' % (service.key.name,),
                'service': 'backend',
            }
            _queue_task(**task)
            logging.debug('Added: %s', task)

    _maybe_transact(do)


def get_payload(request):
    return _deserialize_entity(request.get_data())


def _maybe_transact(fn, *args, **kwargs):
    # We have to fn this "fn" nonsense, because when on dev we fake tasks by
    # just triggering them via http, and the transaction hasn't written the
    # values yet, so the other server can't read them if they get processed
    # before the transaction completes.
    if config.is_dev:
        fn(*args, **kwargs)
    else:
        with ds_util.client.transaction():
            fn(*args, **kwargs)


def process_event(service_key: Key, event):
    return _queue_task(
        name=event.key.name,
        entity=_params_entity(event=event),
        relative_uri='/services/%s/tasks/process_event' % (service_key.name,),
        service='backend',
        parent=_events_parent,
        delay_timedelta=datetime.timedelta(seconds=5),
    )


def process_slack_event(event):
    return _queue_task(
        name=event.key.name,
        entity=_params_entity(event=event),
        relative_uri='/services/slack/tasks/process_event',
        service='backend',
        parent=_slack_events_parent,
    )


def process_weight_trend(event):
    return _queue_task(
        entity=_params_entity(event=event),
        relative_uri='/tasks/process_weight_trend',
        service='backend',
        parent=_notifications_parent,
    )


def process_measure(user_key, measure):
    return _queue_task(
        entity=_params_entity(user_key=user_key, measure=measure),
        relative_uri='/xsync/tasks/process_measure',
        service='backend',
        parent=_events_parent,
    )


def process_backfill(
    source_key: Key, dest_key: Key, start: datetime.datetime, end: datetime.datetime
):
    return _queue_task(
        entity=_params_entity(
            source_key=source_key, dest_key=dest_key, start=start, end=end
        ),
        relative_uri='/xsync/tasks/process_backfill',
        service='backend',
        parent=_backfill_parent,
    )


def process_pubsub_rides(user: Entity, data: dict):
    return _queue_task(
        entity=_params_entity(user=user, data=data),
        relative_uri='/services/google/process/rides',
        service='backend',
        parent=_gmail_parent,
    )


def process_garmin_livetrack(url):
    return _queue_task(
        entity=_params_entity(url=url),
        relative_uri='/services/garmin/process/livetrack',
        service='backend',
        parent=_livetrack_parent,
    )


def task_body_for_test(**kwargs):
    params_entity = _params_entity(**kwargs)
    return _serialize_entity(params_entity)

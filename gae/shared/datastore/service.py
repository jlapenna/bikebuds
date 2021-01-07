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

import datetime
import logging

from google.cloud.datastore.entity import Entity
from google.cloud.datastore.key import Key

from shared import ds_util


class Service(object):
    """Its a service!"""

    @classmethod
    def _set_defaults(cls, service):
        service['sync_state'] = service.get('sync_state', {})
        service['sync_enabled'] = service.get('sync_enabled', True)

    @classmethod
    def get(cls, name: str, parent: Key = None):
        key = ds_util.client.key('Service', name, parent=parent)
        return Service.from_key(key)

    @classmethod
    def from_key(cls, key: Key):
        service = ds_util.client.get(key)
        if not service:
            service = Entity(key)
        Service._set_defaults(service)
        return service

    @classmethod
    def clear_credentials(cls, service):
        cls.update_credentials(service, new_credentials=None)

    @classmethod
    def update_credentials(cls, service, new_credentials):
        if not new_credentials:
            logging.info('Clearing credentials: %s', service.key)
            service.pop('credentials', None)
            ds_util.client.put(service)
            return None

        logging.debug('Updating credentials: %s', service.key)
        service['credentials'] = service.get('credentials', {})
        if service['credentials'] != new_credentials:
            service['credentials'].update(new_credentials)
            logging.info('Updated service credentials: %s', service.key)
            ds_util.client.put(service)
        else:
            logging.info('Unchanged service credentials: %s', service.key)
        return service['credentials']

    @classmethod
    def has_credentials(cls, service, required_key='refresh_token'):
        return bool(
            service is not None
            and service.get('credentials')
            and (required_key is None or service['credentials'].get(required_key))
        )

    @classmethod
    def set_sync_enqueued(cls, service):
        now = datetime.datetime.now(datetime.timezone.utc)
        service['sync_state'] = {
            'updated_at': now,
            'syncing': True,
            'enqueued_at': now,
            'started_at': None,
            'successful': None,
            'error': None,
        }
        ds_util.client.put(service)

    @classmethod
    def set_sync_started(cls, service):
        now = datetime.datetime.now(datetime.timezone.utc)
        service['sync_state'].update(
            {'updated_at': now, 'syncing': True, 'started_at': now}
        )
        ds_util.client.put(service)

    @classmethod
    def set_sync_finished(cls, service, error=None):
        now = datetime.datetime.now(datetime.timezone.utc)
        service['sync_state'].update(
            {
                'updated_at': now,
                'syncing': False,
                'successful': not error,
                'error': error,
            }
        )
        ds_util.client.put(service)

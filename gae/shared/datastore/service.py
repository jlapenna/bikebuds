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

from google.cloud.datastore.entity import Entity

from shared import ds_util


class Service(object):
    """Its a service!"""

    @classmethod
    def get(cls, name, parent=None):
        key = ds_util.client.key('Service', name, parent=parent)
        service = ds_util.client.get(key)
        if service:
            return service
        service = Entity(key)
        service['sync_enabled'] = True
        ds_util.client.put(service)
        return service

    @classmethod
    def update_credentials(cls, service, new_credentials):
        updated = False
        if new_credentials is None or not new_credentials:
            logging.info('Clearing credentials: %s', service.key)
            if 'credentials' in service:
                del service['credentials']
            ds_util.client.put(service)
            return None

        logging.debug('Updating credentials: %s', service.key)
        if 'credentials' not in service or service['credentials'] is None:
            # If we don't have credentials in the service at all, add it,
            # the rest assume the key exists.
            service['credentials'] = {}
        if service['credentials'] != new_credentials:
            service['credentials'].update(new_credentials)
            updated = True
        if updated:
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

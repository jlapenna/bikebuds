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

# Module supporting storing service info.

import logging

from google.appengine.ext import ndb

from endpoints import message_types
from endpoints import messages

from shared.datastore import users


class Service(ndb.Model):
    """Holds service info."""
    _use_memcache = False

    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    credentials = ndb.KeyProperty()
    syncing = ndb.BooleanProperty(default=False)
    sync_date = ndb.DateTimeProperty()
    sync_successful = ndb.BooleanProperty()
    sync_enabled = ndb.BooleanProperty(default=True)

    @classmethod
    def get(cls, user_key, name):
        service_key = cls.get_key(user_key, name)
        service = service_key.get()
        if service is None:
            service = cls(key=service_key)
            r = service.put()
        return service

    @classmethod
    def get_key(cls, user_key, name):
        return ndb.Key(cls, name, parent=user_key)

    @classmethod
    def to_message(cls, service):
        attributes = {}
        for key in cls._properties:
            value = getattr(service, key, None)
            if value is None:
                continue
            if key == 'credentials':
                value = value is not None
            attributes[key] = value
        return ServiceMessage(id=service.key.id(), **attributes)

    def get_credentials(self):
        if self.credentials is not None:
            return self.credentials.get()
        else:
            return None

    @ndb.transactional
    def clear_credentials(self):
        if self.credentials is not None:
            self.credentials.delete()
        self.credentials = None
        self.put()

    @ndb.transactional
    def update_credentials(self, new_credentials):
        self.credentials = ServiceCredentials._update(self, new_credentials).key
        self.put()
        return self.credentials


class ServiceMessage(messages.Message):
    id = messages.StringField(1)

    created = message_types.DateTimeField(2)
    modified = message_types.DateTimeField(3)
    credentials = messages.BooleanField(4)
    syncing = messages.BooleanField(5)
    sync_date = message_types.DateTimeField(6)
    sync_successful = messages.BooleanField(7)
    sync_enabled = messages.BooleanField(8)


class ServiceCredentials(ndb.Expando):
    _use_memcache = False

    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    @ndb.transactional
    def _update(cls, service, new_credentials):
        updated = False
        service_creds = service.get_credentials()
        if service_creds is None:
            updated = True
            service_creds = ServiceCredentials(
                    id=service.key.id(), parent=service.key)
        for k, v in new_credentials.items():
            updated = True
            setattr(service_creds, k, v)
        if updated:
            service_creds.put()
        return service_creds

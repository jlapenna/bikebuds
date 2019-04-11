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

# Module supporting storing user info.

from google.appengine.ext import ndb


class DatastoreState(ndb.Model):
    """Holds user info."""
    _use_memcache = False

    name = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    version = ndb.IntegerProperty()


class SyncState(ndb.Model):
    """Holds overall sync state."""
    _use_memcache = False

    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    total_tasks = ndb.IntegerProperty(indexed=False)
    completed_tasks = ndb.IntegerProperty(indexed=False)


class SubscriptionEvent(ndb.Expando):
    """Holds data related to a subscription event.
    
    Parent should be the service associated with the event.
    """
    _use_memcache = False

    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    processing = ndb.BooleanProperty()


class Message(ndb.Expando):
    id = ndb.StringProperty()
    client_store = ndb.KeyProperty()
    success = ndb.BooleanProperty()


class Notification(Message):
    title = ndb.StringProperty()
    body = ndb.StringProperty()


class Data(Message):
    pass


class FcmMessage(ndb.Model):
    """Holds data related to a notification.
    
    Parent should be the user associated with the event.
    """
    _use_memcache = False

    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    messages = ndb.StructuredProperty(Message, repeated=True)

    def add_delivery(self, client_store, message, response):
        if message.data is not None:
            self.messages.append(
                    Data(
                        id=response,
                        client_store=client_store.key,
                        success=True))
        elif message.notification is not None:
            self.messages.append(
                    Notification(
                        id=response,
                        client_store=client_store.key,
                        success=True,
                        title=message.notification.title,
                        body=message.notification.body))
        else:
            logging.error('Cannot add delivery of unknown message type')

    def add_failure(self, client_store, message, response):
        if message.data is not None:
            self.messages.append(
                    Data(
                        client_store=client_store.key,
                        success=False))
        elif message.notification is not None:
            self.messages.append(
                    Notification(
                        client_store=client_store.key,
                        success=False,
                        title=message.notification.title,
                        body=message.notification.body))
        else:
            logging.error('Cannot add failure of unknown message type')

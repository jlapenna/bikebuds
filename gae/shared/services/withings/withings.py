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
import sys

from google.appengine.ext import ndb

from shared.config import config

from shared.datastore.admin import SubscriptionEvent
from shared.datastore.measures import Measure, Series

import nokia


class Worker(object):

    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        self.sync_measures()
        if not config.is_dev:
            self.sync_subscription()

    def sync_measures(self):
        measures = sorted(
                self.client.get_measures(lastupdate=0, updatetime=0),
                key=lambda x: x.date)
        Series.entity_from_withings(self.service.key, measures).put()

    def sync_subscription(self):
        callback_url = (
                '%s/services/withings/events?sub_secret=%s&service_key=%s' % (
                    config.frontend_url,
                    config.withings_creds['sub_secret'],
                    self.service.key.urlsafe()))
        subscriptions = self.client.list_subscriptions()
        if not subscriptions:
            logging.info('Subscribing: %s to %s',
                    self.service.key, callback_url);
            result = self.client.subscribe(
                    callback_url, comment=self.service.key.urlsafe())
            logging.info('Subscribed: %s to %s -> %s',
                    self.service.key, callback_url, result);

    def remove_subscriptions(self):
        subscriptions = self.client.list_subscriptions()
        for sub in subscriptions:
            logging.info('Unsubscribing: %s', sub)
            try:
                result = self.client.unsubscribe(sub['callbackurl'])
            except Exception, e:
                logging.warn('Unsubscribe failed: %s', sub)


class EventsWorker(object):
    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        measures = sorted(
                self.client.get_measures(lastupdate=0, updatetime=0),
                key=lambda x: x.date)
        @ndb.transactional
        def transact():
            # Ensure we actually fetch all pages of the query, use an iterator.
            batch = [entity.key for entity
                        in SubscriptionEvent.query(ancestor=self.service.key)]
            logging.debug('process_event_batch: %s, count: %s',
                    self.service.key, len(batch))
            Series.entity_from_withings(self.service.key, measures).put()
            ndb.delete_multi(batch)
        transact()


def create_client(service):
    def refresh_callback(new_credentials):
        service.update_credentials(new_credentials)
    return nokia.NokiaApi(service.get_credentials(),
            refresh_cb=refresh_callback)

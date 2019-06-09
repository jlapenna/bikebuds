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

from firebase_admin import messaging

from measurement.measures import Weight
import nokia

from shared import ds_util
from shared import fcm_util
from shared import task_util
from shared.config import config
from shared.datastore.series import Series
from shared.datastore.user import User
from shared.datastore.service import Service

from services.withings.client import create_client


class Worker(object):

    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        self.sync_measures()
        if not config.is_dev:
            self.sync_subscription()

    def sync_measures(self):
        logging.warn('sync_measures')
        measures = sorted(
                self.client.get_measures(lastupdate=0, updatetime=0),
                key=lambda x: x.date)
        series = Series.to_entity(measures, self.service.key.name,
                parent=self.service.key)
        return ds_util.client.put(series)

    def sync_subscription(self):
        callback_url = (
                '%s/services/withings/events?sub_secret=%s&service_key=%s' % (
                    config.frontend_url,
                    config.withings_creds['sub_secret'],
                    self.service.key.to_legacy_urlsafe()))
        subscriptions = self.client.list_subscriptions()
        if not subscriptions:
            logging.info('Subscribing: %s to %s',
                    self.service.key, callback_url)
            result = self.client.subscribe(
                    callback_url, comment=self.service.key.to_legacy_urlsafe())
            logging.info('Subscribed: %s to %s -> %s',
                    self.service.key, callback_url, result)

    def remove_subscriptions(self):
        subscriptions = self.client.list_subscriptions()
        for sub in subscriptions:
            logging.info('Unsubscribing: %s', sub)
            try:
                result = self.client.unsubscribe(sub['callbackurl'])
            except Exception as e:
                logging.warn('Unsubscribe failed: %s', sub)


class EventsWorker(object):

    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        measures = sorted(
                self.client.get_measures(lastupdate=0, updatetime=0),
                key=lambda x: x.date)
        series = Series.to_entity(measures, self.service.key.name,
                parent=self.service.key)

        query = ds_util.client.query(
                kind='SubscriptionEvent', ancestor=self.service.key)
        query.keys_only()
        batch = [entity.key for entity in query.fetch()]
        logging.debug('EventsWorker: process_event_batch: %s, count: %s',
                self.service.key, len(batch))
        ds_util.client.put(series)
        ds_util.client.delete_multi(batch)

        user = ds_util.client.get(self.service.key.parent)
        if user['preferences']['daily_weight_notif']:
            logging.debug('EventsWorker: daily_weight_notif: queued: %s', user.key)
            task_util.process_weight_trend(self.service)
        else:
            logging.debug('EventsWorker: daily_weight_notif: not enabled: %s', user.key)

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

from firebase_admin import messaging

from measurement.measures import Weight
import nokia

from shared import fcm_util
from shared import task_util
from shared.config import config

from shared.datastore.admin import FcmMessage, SubscriptionEvent
from shared.datastore.measures import Series
from shared.datastore.users import User, PreferencesMessage, ClientStore
from shared.datastore.services import Service


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
                    self.service.key, callback_url)
            result = self.client.subscribe(
                    callback_url, comment=self.service.key.urlsafe())
            logging.info('Subscribed: %s to %s -> %s',
                    self.service.key, callback_url, result)

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
        series = Series.entity_from_withings(self.service.key, measures)

        user = ndb.Key('User', self.service.key.parent().id()).get()

        @ndb.transactional
        def transact():
            # Ensure we actually fetch all pages of the query, use an iterator.
            batch = [entity.key for entity
                        in SubscriptionEvent.query(ancestor=self.service.key)]
            logging.debug('process_event_batch: %s, count: %s',
                    self.service.key, len(batch))
            series.put()
            ndb.delete_multi(batch)
            if user.preferences.daily_weight_notif:
                task_util.process_weight_trend(self.service)
        transact()


class WeightTrendWorker(object):

    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        # User info
        user = ndb.Key('User', self.service.key.parent().id()).get()
        if not user.preferences.daily_weight_notif:
            logging.debug('WeightTrendWorker: %s daily_weight_notif: not enabled.', user.key)
            return
        to_imperial = user.preferences.units == PreferencesMessage.Unit.IMPERIAL

        # Trends calculation
        series_entity = Series.get_default(Service.get_key(user.key, 'withings'))
        weight_trend = self._weight_trend(series_entity)
        if not weight_trend:
            logging.debug('WeightTrendWorker: %s daily_weight_notif: no trend', user.key)
            return
        logging.debug('WeightTrendWorker: %s daily_weight_notif: %s.', user.key, weight_trend)
        latest_weight = weight_trend[-1]
        if to_imperial:
            latest_weight = Weight(kg=latest_weight.weight).lb

        # Send notifications
        clients = ClientStore.query(ancestor=user.key)
        def notif_fn(latest_weight, client_store=None):
            return messaging.Message(
                    notification=messaging.Notification(
                        title='Weight Trend',
                        body='Today %.1f' % (latest_weight,),
                        ),
                    android=messaging.AndroidConfig(
                        priority='normal',
                        notification=messaging.AndroidNotification(
                            color='#f45342'
                            ),
                        ),
                    token=client_store.client.id,
                    )
        fcm_util.send(user, clients, notif_fn, latest_weight)

    def _weight_trend(self, series):
        today = datetime.datetime.utcnow()
        week_ago = today - datetime.timedelta(days=7)
        month_ago = today - datetime.timedelta(days=30)
        six_months_ago = today - datetime.timedelta(days=183)
        year_ago = today - datetime.timedelta(days=365)
        ticks = [year_ago, six_months_ago, month_ago, week_ago, today]
        ticks_index = len(ticks) - 1
        measures = []
        new_measures = series.series.measures
        for measure in reversed(new_measures):
            if measure.date <= ticks[ticks_index]:
                measures.insert(0, measure)
                ticks_index -= 1
            if measure.date <= year_ago:
                break
        return measures


def create_client(service):
    def refresh_callback(new_credentials):
        service.update_credentials(new_credentials)
    return nokia.NokiaApi(service.get_credentials(),
            refresh_cb=refresh_callback)

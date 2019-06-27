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
from urllib.parse import urlencode

from google.cloud.datastore.entity import Entity

from firebase_admin import messaging
from measurement.measures import Weight
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError, MissingTokenError
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
        try:
            self.sync_measures()
            self.sync_subscription()
        except TokenExpiredError as e:
            logging.exception('Token Expired Error: service: %s, wiping creds',
                    self.service['credentials']);
            Service.update_credentials(self.service, None)
        except MissingTokenError as e:
            logging.exception('Missing Token Error: service: %s, wiping creds',
                    self.service['credentials']);
            Service.update_credentials(self.service, None)

    def sync_measures(self):
        measures = sorted(
                self.client.get_measures(lastupdate=0, updatetime=0),
                key=lambda x: x.date)
        series = Series.to_entity(measures, self.service.key.name,
                parent=self.service.key)
        ds_util.client.put(series)

    def sync_subscription(self):
        query_string = urlencode({
                'sub_secret': config.withings_creds['sub_secret'],
                'service_key': self.service.key.to_legacy_urlsafe()
        })
        callbackurl = '%s/services/withings/events?%s' % (
            config.frontend_url, query_string)
        comment = self.service.key.to_legacy_urlsafe().decode()
        is_subscribed = self.client.is_subscribed(callbackurl)
        logging.debug('Currently subscribed %s: %s to %s',
                is_subscribed, self.service.key, callbackurl)
        
        # Existing subs.
        subscriptions = self.client.list_subscriptions()
        for sub in subscriptions:
            logging.debug('Examining sub: %s to %s', self.service.key, sub)
            if (config.frontend_url in sub['callbackurl']
                    and sub['callbackurl'] != callbackurl):
                # This sub is bikebuds, but we don't recognize it.
                try:
                    self.client.unsubscribe(sub['callbackurl'])
                    logging.info('Unsubscribed: %s from %s',
                            self.service.key, sub)
                    ds_util.client.delete(
                            ds_util.client.key('WithingsSubscription',
                                sub['callbackurl'], parent=self.service.key))
                except Exception as e:
                    logging.exception('Unsubscribe failed: %s from %s',
                            self.service.key, sub)

        # After previous cleanup, see if we need to re-subscribed:
        is_subscribed = self.client.is_subscribed(callbackurl)
        if is_subscribed:
            logging.debug('Already have a sub, not re-registering for %s to %s',
                    self.service.key, callbackurl)
            sub_entity = Entity(
                    ds_util.client.key('WithingsSubscription',
                        callbackurl, parent=self.service.key))
            sub_entity.update({'callbackurl': callbackurl, 'comment': comment})
            ds_util.client.put(sub_entity)
        elif config.is_dev:
            logging.debug('Dev server. Not registering %s to %s',
                    self.service.key, callbackurl)
        else:
            try:
                self.client.subscribe(callbackurl, comment=comment)
                logging.info('Subscribed: %s to %s', self.service.key,
                        callbackurl)
                entity = Entity(
                        ds_util.client.key('WithingsSubscription',
                            callbackurl, parent=self.service.key))
                entity.update({
                    'callbackurl': callbackurl,
                    'comment': comment,
                    'date': datetime.datetime.now(datetime.timezone.utc)
                    })
                ds_util.client.put(entity)
            except Exception as e:
                logging.exception('Subscribe failed: %s to %s',
                        self.service.key, callbackurl)


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
        ds_util.client.put(series)

        query = ds_util.client.query(
                kind='SubscriptionEvent', ancestor=self.service.key)
        query.keys_only()
        ds_util.client.delete_multi(e.key for e in query.fetch())

        user = ds_util.client.get(self.service.key.parent)
        if user['preferences']['daily_weight_notif']:
            logging.debug('EventsWorker: daily_weight_notif: queued: %s',
                    user.key)
            task_util.process_weight_trend(self.service)
        else:
            logging.debug('EventsWorker: daily_weight_notif: not enabled: %s',
                    user.key)

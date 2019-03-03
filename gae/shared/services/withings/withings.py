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
        self.sync_subscription()

    def sync_measures(self):
        measures = self.client.get_measures(lastupdate=0, updatetime=0)

        @ndb.transactional
        def put_series():
            Series.entity_from_withings(self.service.key, measures).put()
        return put_series()

    def sync_subscription(self):
        #frontend_url = config.frontend_url
        frontend_url = 'https://www.bikebuds.cc'
        callback_url = (
                '%s/services/withings/events?sub_secret=%s&service_key=%s' % (
                    frontend_url,
                    config.withings_creds['sub_secret'],
                    self.service.key.urlsafe()))
        # Throws an exception on error... TODO: handle this.
        result = self.client.subscribe(callback_url, comment=self.service.key.urlsafe())
        logging.info('Subscription result: %s-> %s', callback_url, result);


class EventsWorker(object):
    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        events = SubscriptionEvent.query(
                ancestor=self.service.key)  #.order(-ndb.GenericProperty('event_time'))
        batch = [event for event in events]
        @ndb.transactional
        def transact():
            logging.debug('process_event_batch: %s, %s', self.service.key, len(batch))
            measures = self.client.get_measures(lastupdate=0, updatetime=0)
            Series.entity_from_withings(self.service.key, measures).put()
            ndb.delete_multi((event.key for event in batch))
        transact()



def create_client(service):
    def refresh_callback(new_credentials):
        service.update_credentials(new_credentials)
    return nokia.NokiaApi(service.get_credentials(),
            refresh_cb=refresh_callback)

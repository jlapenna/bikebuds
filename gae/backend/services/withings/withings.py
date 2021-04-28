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
import heapq
import logging
from urllib.parse import urlencode

import flask

from withings_api.common import MeasureGetMeasGroupCategory
from withings_api.common import InvalidParamsException

from shared import ds_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.series import Measure, Series
from shared.datastore.service import Service
from shared.datastore.subscription import Subscription
from shared.datastore.user import User
from shared.exceptions import SyncException
from shared.services.withings import client

import sync_helper
from services.withings.weight_trend_notif import WeightTrendWorker


module = flask.Blueprint('withings', __name__)


@module.route('/tasks/sync', methods=['POST'])
def sync():
    logging.debug('Syncing: withings')
    params = task_util.get_payload(flask.request)

    service = ds_util.client.get(params['service_key'])
    if not Service.has_credentials(service):
        logging.warning('No creds: %s', service.key)
        Service.set_sync_finished(service, error='No credentials')
        return responses.OK_NO_CREDENTIALS

    try:
        Service.set_sync_started(service)
        sync_helper.do(Worker(service), work_key=service.key)
        Service.set_sync_finished(service)
        return responses.OK
    except SyncException as e:
        Service.set_sync_finished(service, error=str(e))
        return responses.OK_SYNC_EXCEPTION


@module.route('/tasks/event', methods=['POST'])
def process_event_task():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('Event: %s', event.key)

    # First try to get the service using the event.key's service.
    # If this event is coming from an old subscription / secret url, which
    # embeds a service_key in it, then we might get these.
    service_key = event.key.parent
    service = ds_util.client.get(service_key)

    if service is None:
        logging.error('Event: No service: %s', event.key)
        return responses.OK_NO_SERVICE

    if not Service.has_credentials(service):
        logging.warning('Event: No credentials: %s', event.key)
        return responses.OK_NO_CREDENTIALS

    try:
        sync_helper.do(EventsWorker(service, event), work_key=event.key)
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


@module.route('/tasks/weight_trend', methods=['POST'])
def withings_tasks_weight_trend_task():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('WeightTrendEvent: %s', event.key)
    service_key = event.key.parent
    service = ds_util.client.get(service_key)

    if service is None:
        logging.error('WeightTrendEvent: No service: %s', event.key)
        return responses.OK_NO_SERVICE

    try:
        if service.key.name == 'withings':
            sync_helper.do(WeightTrendWorker(service, event), work_key=event.key)
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


class Worker(object):
    def __init__(self, service):
        self.service = service
        self.client = client.create_client(service)

    def sync(self):
        self.sync_measures()
        self.sync_subscription()

    def sync_measures(self):
        measures = sorted(
            self.client.measure_get_meas(
                category=MeasureGetMeasGroupCategory.REAL,
                startdate=None,
                enddate=None,
                lastupdate=0,
            ).measuregrps,
            key=lambda x: x.date,
        )
        series = Series.to_entity(measures, parent=self.service.key)
        ds_util.client.put(series)

    def sync_subscription(self):
        query_string = urlencode(
            {
                'sub_secret': config.withings_creds['sub_secret'],
                'service_key': self.service.key.to_legacy_urlsafe(),
            }
        )
        callbackurl = '%s/services/withings/events?%s' % (
            config.frontend_url,
            query_string,
        )
        comment = self.service.key.to_legacy_urlsafe().decode()
        try:
            sub = self.client.notify_get(callbackurl)
        except InvalidParamsException:
            sub = None
        logging.debug(
            'Current sub: %s to %s for %s', self.service.key, sub, callbackurl
        )

        self._revoke_unknown_subscriptions(callbackurl)

        # After previous cleanup, see if we need to re-subscribed:
        try:
            sub = self.client.notify_get(callbackurl)
        except InvalidParamsException:
            sub = None

        if sub:
            self._store_sub(sub.callbackurl, sub.comment)
        elif config.is_dev:
            logging.debug(
                'Dev server. Not registering %s to %s', self.service.key, callbackurl
            )
        else:
            self._subscribe(callbackurl, comment)

    def _revoke_unknown_subscriptions(self, callbackurl):
        # Existing subs.
        notify_response = self.client.notify_list()
        for sub in notify_response.profiles:
            logging.debug('Examining sub: %s to %s', self.service.key, sub)
            if (
                config.frontend_url in sub.callbackurl
                and sub.callbackurl != callbackurl
            ):
                # This sub is bikebuds, but we don't recognize it.
                try:
                    self.client.notify_revoke(sub.callbackurl)
                    logging.info('Unsubscribed: %s from %s', self.service.key, sub)
                    ds_util.client.delete(
                        ds_util.client.key(
                            'Subscription', sub.callbackurl, parent=self.service.key
                        )
                    )
                except Exception:
                    logging.exception(
                        'Unsubscribe failed: %s from %s', self.service.key, sub
                    )

    def _subscribe(self, callbackurl, comment):
        try:
            self.client.notify_subscribe(callbackurl, comment=comment)
            logging.info('Subscribed: %s to %s', self.service.key, callbackurl)
            self._store_sub(callbackurl, comment)
        except Exception:
            logging.exception(
                'Subscribe failed: %s to %s', self.service.key, callbackurl
            )

    def _store_sub(self, callbackurl, comment):
        sub_entity = Subscription.to_entity(
            {
                'callbackurl': callbackurl,
                'comment': comment,
                'date': datetime.datetime.now(datetime.timezone.utc),
            },
            callbackurl,
            parent=self.service.key,
        )
        logging.debug('Stored: %s to %s', self.service.key, sub_entity)
        ds_util.client.put(sub_entity)


class EventsWorker(object):
    def __init__(self, service, event):
        self.service = service
        self.event = event
        self.client = client.create_client(service)

    def sync(self):
        # Clear out old subscription events.
        query = ds_util.client.query(
            kind='SubscriptionEvent', ancestor=self.service.key.parent
        )
        recent = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        query.add_filter('date', '<', recent)
        query.keys_only()
        ds_util.client.delete_multi([r.key for r in query.fetch()])

        # Withings likes to send us dupes. Lets ignore them if we've seen them too recently.
        if ds_util.client.get(self.event.key) is not None:
            logging.info('Skipping duplicate Event: %s', self.event)
            return
        else:
            ds_util.client.put(self.event)

        series = Series.get(self.service.key)
        series['measures'] = series.get('measures', [])
        logging.debug('Measures length before: %s', len(series['measures']))

        new_measures = [
            Measure.to_entity(m, self.service.key)
            for m in self.client.measure_get_meas(
                category=MeasureGetMeasGroupCategory.REAL,
                startdate=datetime.datetime.utcfromtimestamp(
                    int(self.event['event_data']['startdate'])
                ),
                enddate=datetime.datetime.utcfromtimestamp(
                    int(self.event['event_data']['enddate'])
                ),
            ).measuregrps
        ]
        logging.debug('Found %s new measures', len(new_measures))

        # Remove any measures with dates we just fetched.
        series['measures'] = [
            m
            for m in filter(
                lambda x: x['date'] not in (nm['date'] for nm in new_measures),
                series['measures'],
            )
        ]

        logging.debug('Measures length filtered: %s', len(series['measures']))

        # Merge the two sorted lists.
        series['measures'] = [
            m
            for m in heapq.merge(
                series['measures'], new_measures, key=lambda x: x['date']
            )
        ]
        logging.debug('Measures length after: %s', len(series['measures']))

        # Store the updated measures.
        ds_util.client.put(series)
        logging.debug('WithingsEvent: Updated series: %s', self.event.key)

        # Possibly fire off down-stream events.
        user = User.get(self.service.key.parent)
        if user['preferences']['daily_weight_notif']:
            logging.debug(
                'WithingsEvent: daily_weight_notif: Queued: %s: %s',
                user.key,
                self.event.key,
            )
            task_util.withings_tasks_weight_trend(self.event)
        if user['preferences']['sync_weight']:
            logging.debug(
                'WithingsEvent: ProcessMeasure: Queued: %s: %s',
                user.key,
                self.event.key,
            )
            for measure in new_measures:
                task_util.xsync_tasks_measure(user.key, measure)

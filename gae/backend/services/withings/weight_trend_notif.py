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

from firebase_admin import messaging

from measurement.measures import Weight
import nokia

from shared import ds_util
from shared import fcm_util
from shared.datastore.series import Series
from shared.datastore.user import Preferences

from services.withings.client import create_client


class WeightTrendWorker(object):

    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        user = ds_util.client.get(self.service.key.parent)
        if not user['preferences']['daily_weight_notif']:
            logging.debug('WeightTrendWorker: %s daily_weight_notif: not enabled.', user.key)
            return
        to_imperial = user['preferences']['units'] == Preferences.Units.IMPERIAL

        # Trends calculation
        series_entity = Series.get('withings', self.service.key)
        weight_trend = self._weight_trend(series_entity)
        if not weight_trend:
            logging.debug('WeightTrendWorker: %s daily_weight_notif: no trend', user.key)
            return
        logging.debug('WeightTrendWorker: %s daily_weight_notif: %s.', user.key, weight_trend)
        latest_weight = weight_trend[-1]
        if to_imperial:
            latest_weight = Weight(kg=latest_weight['weight']).lb

        # Send notifications
        clients = fcm_util.active_clients(user.key)
        def notif_fn(latest_weight, client=None):
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
                    token=client['token'],
                    )
        fcm_util.send(user.key, clients, notif_fn, latest_weight)

    def _weight_trend(self, series):
        today = datetime.datetime.now(datetime.timezone.utc)
        week_ago = today - datetime.timedelta(days=7)
        month_ago = today - datetime.timedelta(days=30)
        six_months_ago = today - datetime.timedelta(days=183)
        year_ago = today - datetime.timedelta(days=365)
        ticks = [year_ago, six_months_ago, month_ago, week_ago, today]
        ticks_index = len(ticks) - 1
        measures = []
        for measure in reversed(series['measures']):
            logging.debug('DATE: %s, %s', measure['date'], (measure['date'].tzinfo == None))
            logging.debug('TICK: %s, %s', ticks[ticks_index], (ticks[ticks_index].tzinfo == None))
            if measure['date'] <= ticks[ticks_index]:
                measures.insert(0, measure)
                ticks_index -= 1
            if measure['date'] <= year_ago:
                break
        return measures

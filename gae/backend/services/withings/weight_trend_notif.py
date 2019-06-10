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

import collections
import datetime
import logging

from firebase_admin import messaging

from babel.dates import format_datetime, format_date
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
            logging.debug('WeightTrendWorker: daily_weight_notif: not enabled: %s', user.key)
            return
        to_imperial = user['preferences']['units'] == Preferences.Units.IMPERIAL

        # Calculate the trend.
        series_entity = Series.get('withings', self.service.key)
        weight_trend = self._weight_trend(series_entity)

        time_frame = None
        if 'a week ago' in weight_trend:
            time_frame = 'a week ago'
        elif 'a month ago' in weight_trend:
            time_frame = 'a month ago'
        elif 'six months ago' in weight_trend:
            time_frame = 'six months ago'
        elif 'a year ago' in weight_trend:
            time_frame = 'a year ago'

        if time_frame is None:
            logging.debug(
                    'WeightTrendWorker: daily_weight_notif: no timeframe: %s', user.key)
            return

        latest_weight = weight_trend['latest'][1]['weight']
        if to_imperial:
            latest_weight = Weight(kg=latest_weight).lb
        time_frame_weight = weight_trend[time_frame][1]['weight']

        if to_imperial:
            time_frame_weight = Weight(kg=time_frame_weight).lb
        time_frame_date = weight_trend[time_frame][1]['date']

        delta = latest_weight - time_frame_weight
        unit = 'kg'
        if to_imperial:
            unit = 'lbs'
        if delta > 0:
            title = 'Down %.1f %s from %s' % (abs(delta), unit, time_frame)
        if delta == 0:
            title = 'Weight unchanged since last week'
        else:
            title = 'Up %.1f %s from %s' % (abs(delta), unit, time_frame)
        body = 'You were %.1f %s on %s' % (time_frame_weight, unit,
                format_date(time_frame_date.date(), format='medium'))

        # Send notifications
        clients = fcm_util.best_clients(user.key)
        def notif_fn(client=None):
            return messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                        ),
                    android=messaging.AndroidConfig(
                        priority='normal',
                        notification=messaging.AndroidNotification(
                            color='#f45342'
                            ),
                        ),
                    token=client['token'],
                    )
        fcm_util.send(user.key, clients, notif_fn)

    def _weight_trend(self, series):
        """Find a series of weights across various time intervals.

        Returns: {'time_frame': [time_frame_date, measure]}
        """

        today = datetime.datetime.now(datetime.timezone.utc)

        trend = [
                ('a year_ago', today - datetime.timedelta(days=365)),
                ('six months ago', today - datetime.timedelta(days=183)),
                ('a month ago', today - datetime.timedelta(days=30)),
                ('a week ago', today - datetime.timedelta(days=7)),
                ('latest', datetime.datetime.now(datetime.timezone.utc)),
                ]

        trend_result = {}

        trend_index = 0
        time_frame, tick = trend[trend_index]
        for measure in series['measures']:
            if measure['date'] > tick:
                # we've come newer than the tick, we need a smaller tick.
                trend_index += 1
                time_frame, tick = trend[trend_index]
            if measure['date'] <= tick:
                trend_result[time_frame] = tick, measure
        return trend_result

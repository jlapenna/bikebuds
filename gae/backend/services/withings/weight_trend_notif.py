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

from babel.dates import format_date
from measurement.measures import Weight

from shared import ds_util
from shared import fcm_util
from shared.datastore.series import Series
from shared.datastore.user import Preferences
from shared.services.withings import client as withings_client


def get_now():
    return datetime.datetime.now(datetime.timezone.utc)


class WeightTrendWorker(object):
    def __init__(self, service, event):
        self.service = service
        self.event = event
        self.client = withings_client.create_client(service)

    def sync(self):
        user = ds_util.client.get(self.service.key.parent)
        if not user['preferences']['daily_weight_notif']:
            logging.debug(
                'WeightTrendWorker: daily_weight_notif: not enabled: %s, %s',
                user.key,
                self.event.key,
            )
            return
        to_imperial = user['preferences']['units'] == Preferences.Units.IMPERIAL

        # Calculate the trend.
        series_entity = Series.get('withings', self.service.key)
        weight_trend = self._weight_trend(series_entity)

        time_frame = self._get_best_time_frame(weight_trend)
        if time_frame is None:
            logging.debug(
                'WeightTrendWorker: daily_weight_notif: no timeframe: %s: %s',
                user.key,
                self.event.key,
            )
            return

        if 'latest' not in weight_trend:
            logging.debug(
                'WeightTrendWorker: daily_weight_notif: no latest: %s: %s',
                user.key,
                self.event.key,
            )
            return

        latest_weight = weight_trend['latest']['weight']
        if to_imperial:
            latest_weight = Weight(kg=latest_weight).lb
        time_frame_weight = weight_trend[time_frame]['weight']

        if to_imperial:
            time_frame_weight = Weight(kg=time_frame_weight).lb
        time_frame_date = weight_trend[time_frame]['date']

        delta = round(latest_weight - time_frame_weight, 1)
        unit = 'kg'
        if to_imperial:
            unit = 'lbs'
        if delta > 0:
            title = 'Up %.1f %s from %s' % (abs(delta), unit, time_frame)
        elif delta == 0:
            title = 'Weight unchanged since %s' % (time_frame,)
        else:
            title = 'Down %.1f %s from %s' % (abs(delta), unit, time_frame)
        body = 'You were %.1f %s on %s' % (
            time_frame_weight,
            unit,
            format_date(time_frame_date.date(), format='medium'),
        )

        # Find the best clients to send the message to.
        clients = fcm_util.best_clients(user.key)

        # Send the messages
        def notif_fn(client=None):
            return messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data={'refresh': 'weight'},
                android=messaging.AndroidConfig(
                    priority='high',  # Wake up the device to notify.
                    ttl=82800,  # 23 hours
                    # notification=messaging.AndroidNotification(),
                ),
                token=client['token'],
            )

        fcm_util.send(self.event.key, clients, notif_fn)

    def _weight_trend(self, series):
        """Find a series of weights across various time intervals.

        Returns: {'time_frame': [time_frame_date, measure]}
        """
        today = get_now().date()

        trend = [
            ('a year ago', today - datetime.timedelta(days=365)),
            ('six months ago', today - datetime.timedelta(days=183)),
            ('a month ago', today - datetime.timedelta(days=30)),
            ('a week ago', today - datetime.timedelta(days=7)),
            ('latest', today),
        ]

        trend_result = {}

        trend_index = 0
        time_frame, tick = trend[trend_index]
        for measure in series['measures']:
            while measure['date'].date() > tick:
                # we've come newer than the tick, we need a smaller tick.
                trend_index += 1
                time_frame, tick = trend[trend_index]
            if measure['date'].date() <= tick:
                if 'weight' in measure:
                    trend_result[time_frame] = measure
        return trend_result

    def _get_best_time_frame(self, weight_trend):
        if 'a week ago' in weight_trend:
            return 'a week ago'
        elif 'a month ago' in weight_trend:
            return 'a month ago'
        elif 'six months ago' in weight_trend:
            return 'six months ago'
        elif 'a year ago' in weight_trend:
            return 'a year ago'
        return None

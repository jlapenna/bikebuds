# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import mock
import unittest

from google.cloud.datastore.entity import Entity

from shared import ds_util

from services.withings.weight_trend_notif import WeightTrendWorker


class WeightTrendWorkerTest(unittest.TestCase):
    @mock.patch('shared.fcm_util.send')
    @mock.patch('shared.fcm_util.best_clients')
    @mock.patch('services.withings.weight_trend_notif.get_now')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    @mock.patch('shared.services.withings.client.create_client')
    def test_one_week_ago(
        self,
        create_client_mock,
        ds_util_client_get_mock,
        ds_util_client_put_mock,
        get_now_mock,
        fcm_util_best_clients_mock,
        fcm_util_send_mock,
    ):
        now = datetime.datetime(2020, 9, 25, 7, 13, tzinfo=datetime.timezone.utc)
        get_now_mock.return_value = now

        measures = []

        measures.insert(0, Entity())
        measures[0].update({'date': now, 'weight': 30})

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 24, 7, 13, tzinfo=datetime.timezone.utc
                ),
                'weight': 35,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 23, 7, 13, tzinfo=datetime.timezone.utc
                ),
                'weight': 40,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 22, 7, 13, tzinfo=datetime.timezone.utc
                ),
                'weight': 45,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 19, 7, 13, tzinfo=datetime.timezone.utc
                ),
                'weight': 50,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 18, 7, 12, tzinfo=datetime.timezone.utc
                ),
                'weight': 54,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 18, 7, 13, tzinfo=datetime.timezone.utc
                ),
                'weight': 55,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 18, 7, 14, tzinfo=datetime.timezone.utc
                ),
                'weight': 56,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 17, 7, 13, tzinfo=datetime.timezone.utc
                ),
                'weight': 60,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 5, 18, 8, 12, tzinfo=datetime.timezone.utc
                ),
                'weight': 60,
            }
        )

        worker = self._setup_side_effects(
            create_client_mock,
            ds_util_client_get_mock,
            ds_util_client_put_mock,
            fcm_util_best_clients_mock,
            fcm_util_send_mock,
            measures,
        )
        worker.sync()

        self._assert_send(
            fcm_util_send_mock,
            'Down 24.0 kg from a week ago',
            'You were 54.0 kg on Sep 18, 2020',
        )

    @mock.patch('shared.fcm_util.send')
    @mock.patch('shared.fcm_util.best_clients')
    @mock.patch('services.withings.weight_trend_notif.get_now')
    @mock.patch('shared.ds_util.client.put')
    @mock.patch('shared.ds_util.client.get')
    @mock.patch('shared.services.withings.client.create_client')
    def test_one_year_ago(
        self,
        create_client_mock,
        ds_util_client_get_mock,
        ds_util_client_put_mock,
        get_now_mock,
        fcm_util_best_clients_mock,
        fcm_util_send_mock,
    ):
        now = datetime.datetime(2020, 9, 25, 7, 13, tzinfo=datetime.timezone.utc)
        get_now_mock.return_value = now

        measures = []

        measures.insert(0, Entity())
        measures[0].update({'date': now, 'weight': 30})

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2020, 9, 24, 7, 13, tzinfo=datetime.timezone.utc
                ),
                'weight': 35,
            }
        )

        measures.insert(0, Entity())
        measures[0].update(
            {
                'date': datetime.datetime(
                    2019, 5, 18, 8, 12, tzinfo=datetime.timezone.utc
                ),
                'weight': 60,
            }
        )

        worker = self._setup_side_effects(
            create_client_mock,
            ds_util_client_get_mock,
            ds_util_client_put_mock,
            fcm_util_best_clients_mock,
            fcm_util_send_mock,
            measures,
        )
        worker.sync()

        self._assert_send(
            fcm_util_send_mock,
            'Down 30.0 kg from a year ago',
            'You were 60.0 kg on May 18, 2019',
        )

    def _setup_side_effects(
        self,
        create_client_mock,
        ds_util_client_get_mock,
        ds_util_client_put_mock,
        fcm_util_best_clients_mock,
        fcm_util_send_mock,
        measures,
    ):
        user = Entity(ds_util.client.key('User', 'someuser'))
        user['preferences'] = {'daily_weight_notif': True, 'units': 'METRIC'}
        service = Entity(ds_util.client.key('Service', 'withings', parent=user.key))
        service['credentials'] = {'refresh_token': 'validrefreshtoken'}
        event_entity = Entity(
            ds_util.client.key('SubscriptionEvent', 'Event', parent=service.key)
        )

        series = Entity(ds_util.client.key('Series', 'withings', parent=service.key))
        series['measures'] = measures

        # There are gets we need to account for.
        def get_side_effect(key):
            if key.name == 'someuser':
                return user
            elif key.name == 'withings':
                return series

        ds_util_client_get_mock.side_effect = get_side_effect

        return WeightTrendWorker(service, event_entity)

    def _assert_send(self, mock, title, body):
        mock.assert_called_once()
        send_args, send_kwargs = mock.call_args
        message = send_args[-1]({'token': 'XYZ_TOKEN'})

        self.assertEqual(message.notification.title, title)
        self.assertEqual(message.notification.body, body)

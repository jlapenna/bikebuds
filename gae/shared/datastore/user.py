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

from google.cloud.datastore.entity import Entity

from shared import ds_util


class Preferences(object):
    class Units(object):
        UNKNOWN = 'UNKNOWN'
        IMPERIAL = 'IMPERIAL'
        METRIC = 'METRIC'

    class WeightService(object):
        UNKNOWN = 'UNKNOWN'
        WITHINGS = 'WITHINGS'
        FITBIT = 'FITBIT'

    @classmethod
    def default(cls):
        return {
            'units': Preferences.Units.IMPERIAL,
            'weight_service': Preferences.WeightService.WITHINGS,
            'daily_weight_notif': False,
        }


class User(object):
    """Its a user!"""

    @classmethod
    def get(cls, claims):
        key = ds_util.client.key('User', claims['sub'])
        user = ds_util.client.get(key)
        if user:
            return user

        # Creating a new user.
        user = Entity(key)
        user['preferences'] = Preferences.default()
        ds_util.client.put(user)
        return user

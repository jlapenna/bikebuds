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
from google.cloud.datastore.key import Key

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
        GARMIN = 'GARMIN'

    @classmethod
    def default(cls):
        return {
            'units': Preferences.Units.IMPERIAL,
            'weight_service': Preferences.WeightService.WITHINGS,
            'daily_weight_notif': False,
            'sync_weight': True,
        }


class User(object):
    """Its a user!"""

    @classmethod
    def _set_defaults(cls, user):
        # Get the default prefs.
        prefs = Preferences.default()
        # Replace the defaults with a uer's saved prefs.
        prefs.update(user.get('preferences', {}))
        # Store the unioned prefs as the user's prefs.
        user['preferences'] = prefs

    @classmethod
    def get(cls, key_or_claims):
        if isinstance(key_or_claims, Key):
            return User.from_uid(key_or_claims.name)
        else:
            return User.from_uid(key_or_claims['sub'])

    @classmethod
    def from_uid(cls, uid):
        key = ds_util.client.key('User', uid)
        user = ds_util.client.get(key)
        if not user:
            user = Entity(key)
        User._set_defaults(user)
        return user

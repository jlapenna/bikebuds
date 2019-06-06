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

import logging

from google.cloud.datastore.entity import Entity

from shared import ds_util
from shared.datastore.strava.converters import StravaConverters

class Athlete(object):
    """Its a athlete!"""

    @classmethod
    def get_by_id(cls, strava_id):
        athlete_query = ds_util.client.query(kind='Athlete')
        athlete_query.filter('id', '=', strava_id)
        athletes = athlete_query.fetch()
        if len(athletes) == 0:
            return None
        elif len(athletes) > 1:
            raise Exception('More athletes than expected.')
        return athletes[0]

    @classmethod
    def get_private(cls, service_key):
        result = [r for r in
                ds_util.client.query(kind='Athlete', ancestor=service_key).fetch()]
        if len(result) == 0:
            return None
        elif len(result) > 1:
            raise Error('Too may athletes for user: %s', service_key.parent)
        else:
            return result[0]

    @classmethod
    def to_entity(cls, athlete, parent=None):
        return StravaConverters.Athlete.to_entity(athlete, parent=parent)

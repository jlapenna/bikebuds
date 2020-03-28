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
from shared.datastore.bbfitbit.converters import FitbitConverters
from shared.datastore.garmin.converters import GarminConverters
from shared.datastore.withings.converters import WithingsConverters


class Series(object):
    """Its a series!"""

    @classmethod
    def get(cls, parent):
        return ds_util.client.get(
            ds_util.client.key('Series', parent.name, parent=parent)
        )

    @classmethod
    def to_entity(cls, measures, parent):
        series = Entity(ds_util.client.key('Series', parent.name, parent=parent))
        series['measures'] = [
            Measure.to_entity(measure, parent) for measure in measures
        ]
        return series


class Measure(object):
    """Its a measure!"""

    @classmethod
    def to_entity(cls, measure, parent):
        if parent.name == 'withings':
            to_entity = WithingsConverters.Measure.to_entity
        elif parent.name == 'fitbit':
            to_entity = FitbitConverters.TimeseriesMeasure.to_entity
        elif parent.name == 'garmin':
            to_entity = GarminConverters.Measure.to_entity
        return to_entity(measure)

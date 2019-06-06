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

from google.cloud.datastore.entity import Entity

import nokia

from shared import ds_util
from shared.datastore.withings.converters import WithingsConverters
from shared.datastore.bbfitbit.converters import FitbitConverters


class Series(object):
    """Its a series!"""

    @classmethod
    def get(cls, name, parent=None):
        return ds_util.client.get(
                ds_util.client.key('Series', name, parent=parent))

    @classmethod
    def to_entity(cls, measures, name, parent=None):
        series = Entity(ds_util.client.key('Series', name, parent=parent))
        measures_entities = []

        if name == 'withings':
            to_entity = WithingsConverters.Measure.to_entity
        elif name == 'fitbit':
            to_entity = FitbitConverters.TimeseriesMeasure.to_entity

        for measure in measures:
            measures_entities.append(to_entity(measure))
        series['measures'] = measures_entities
        return series

    @classmethod
    def _measure_from_withings(cls, measure):
        attributes = dict()
        for key, type_int in nokia.NokiaMeasureGroup.MEASURE_TYPES:
            value = measure.get_measure(type_int)
            if value is not None:
                attributes[key] = value
        entity = Entity(ds_util.client.key('Measure', measure.date.timestamp))
        entity.update(attributes)
        entity['date'] = measure.date.datetime.replace(tzinfo=None)
        return entity

    @classmethod
    def _measure_from_fitbit_time_series(cls, measure):
        date = datetime.datetime.strptime(measure['dateTime'], '%Y-%m-%d')
        entity = Entity(ds_util.client.key('Measure', date.strftime('%s')))
        entity.update(dict(
                date=date,
                weight=float(measure['value']),
                ))
        return entity

    @classmethod
    def _measure_from_fitbit_log(cls, measure):
        date = datetime.datetime.strptime(
                measure['date'] + ' ' + measure['time'], '%Y-%m-%d %H:%M:%S')
        entity = Entity(ds_util.client.key('Measure', date.strftime('%s')))
        entity.update(dict(
                id=measure['logId'],
                date=date,
                weight=measure['weight'],
                fat_ratio=measure['fat'],
                ))
        return entity

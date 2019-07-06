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

from google.cloud.datastore.entity import Entity


from shared import ds_util


class _TimeseriesMeasureConverter(object):
    @classmethod
    def to_entity(cls, measure, parent=None):
        date = datetime.datetime.strptime(measure['dateTime'], '%Y-%m-%d')
        entity = Entity(
            ds_util.client.key('Measure', date.strftime('%s'), parent=parent)
        )
        entity.update(dict(date=date, weight=float(measure['value'])))
        return entity


class _LogMeasureConverter(object):
    @classmethod
    def to_entity(cls, measure, parent=None):
        date = datetime.datetime.strptime(
            measure['date'] + ' ' + measure['time'], '%Y-%m-%d %H:%M:%S'
        )
        entity = Entity(
            ds_util.client.key('Measure', date.strftime('%s'), parent=parent)
        )
        entity.update(
            dict(
                id=measure['logId'],
                date=date,
                weight=measure['weight'],
                fat_ratio=measure['fat'],
            )
        )
        return entity


class FitbitConverters(object):
    LogMeasure = _LogMeasureConverter
    TimeseriesMeasure = _TimeseriesMeasureConverter

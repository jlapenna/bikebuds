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

import withings_api

from shared import ds_util


class _MeasureConverter(object):
    @classmethod
    def to_entity(cls, measure, parent=None):
        attributes = dict()
        for key, type_int in withings_api.WithingsMeasureGroup.MEASURE_TYPES:
            value = measure.get_measure(type_int)
            if value is not None:
                attributes[key] = value
        entity = Entity(
            ds_util.client.key('Measure', measure.date.timestamp, parent=parent)
        )
        entity.update(attributes)
        entity['date'] = measure.date.datetime.replace(tzinfo=None)
        return entity


class WithingsConverters(object):
    Measure = _MeasureConverter

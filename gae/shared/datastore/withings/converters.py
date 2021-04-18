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


class _MeasureConverter(object):
    @classmethod
    def to_entity(cls, measure_group, parent=None):
        """
        MeasureGetMeasGroup(
            attrib=<MeasureGetMeasGroupAttrib.MANUAL_USER_ENTRY: 2>,
            category=<MeasureGetMeasGroupCategory.REAL: 1>,
            created=<Arrow [2019-03-03T17:20:12-08:00]>,
            date=<Arrow [2018-07-19T16:20:00-07:00]>,
            deviceid=None, grpid=1385164716,
            measures=(
                MeasureGetMeasMeasure(type=<MeasureType.WEIGHT: 1>, unit=-2, value=7529),)
        )
        """
        attributes = dict()
        for m in measure_group.measures:
            if m.value is not None:
                attributes[m.type.name.lower()] = m.value * (10 ** m.unit)
        date = measure_group.date.datetime.replace(tzinfo=datetime.timezone.utc)
        entity = Entity(
            ds_util.client.key('Measure', int(date.timestamp()), parent=parent)
        )
        entity.update(attributes)
        entity['date'] = date
        return entity


class WithingsConverters(object):
    Measure = _MeasureConverter

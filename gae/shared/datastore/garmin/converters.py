# Copyright 2020 Google LLC
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
    def to_entity(cls, item):
        attributes = {
            'date': datetime.datetime.utcfromtimestamp(item['timestampGMT'] / 1000),
            'fat_ratio': item['bodyFat'],
            'weight': round(item['weight'] / 1000, 4),
        }
        entity = Entity(ds_util.client.key('Measure'))
        entity.update(attributes)
        return entity


class GarminConverters(object):
    Measure = _MeasureConverter

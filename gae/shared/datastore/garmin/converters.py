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

import copy
import datetime

from google.cloud.datastore.entity import Entity
from sortedcontainers import SortedSet

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


class _TrackConverter(object):
    __ALL_FIELDS = SortedSet(
        [
            'url',
            'url_info',
            'info',
            'status',
        ]
    )
    __INCLUDE_IN_INDEXES = SortedSet(
        [
            'status',
        ]
    )

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, track, parent=None):
        props = copy.deepcopy(track)

        entity = Entity(
            ds_util.client.key('Track', track['url'], parent=parent),
            exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
        )
        entity.update(props)
        return entity


class GarminConverters(object):
    Measure = _MeasureConverter
    Track = _TrackConverter

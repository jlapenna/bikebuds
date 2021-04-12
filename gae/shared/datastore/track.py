# Copyright 2021 Google LLC
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
from shared.datastore.garmin.converters import GarminConverters

from shared import ds_util


class Track(object):
    """Its a track!"""

    STATUS_FAILED = -1
    STATUS_UNKNOWN = 0
    STATUS_INFO = 1
    STATUS_STARTED = 3
    STATUS_FINISHED = 4

    @classmethod
    def get(cls, track_id) -> Entity:
        return ds_util.client.get(ds_util.client.key('Track', int(track_id)))

    @classmethod
    def to_entity(cls, track, parent=None) -> Entity:
        return GarminConverters.Track.to_entity(track, parent=parent)

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


def to_entity(kind, properties, name=None, parent=None, include_in_indexes=tuple()):
    if name:
        key = ds_util.client.key(kind, name, parent=parent)
    else:
        key = ds_util.client.key(kind, parent=parent)
    entity = Entity(key)
    entity.update(properties)
    entity.exclude_from_indexes = entity.keys() - include_in_indexes
    return entity

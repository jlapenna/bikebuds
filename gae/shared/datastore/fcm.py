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

from shared import ds_util
from shared.datastore.entity_util import to_entity


class FcmSendEvent(object):
    @classmethod
    def to_entity(cls, properties, parent=None):
        return to_entity(
            'FcmSendEvent', properties, parent=parent, include_in_indexes=('date',)
        )


class FcmMessage(object):
    @classmethod
    def get(cls, name, parent=None):
        return ds_util.client.get(ds_util.client.key('FcmMessage', name, parent=parent))

    @classmethod
    def to_entity(cls, properties, parent=None):
        return to_entity(
            'FcmMessage', properties, parent=parent, include_in_indexes=('date',)
        )

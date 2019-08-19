# Copyright 2019 Google LLC
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

import hashlib

from shared.datastore.entity_util import to_entity


class Subscription(object):
    @classmethod
    def to_entity(cls, properties, name, parent=None):
        return to_entity(
            'Subscription',
            properties,
            name=name,
            parent=parent,
            include_in_indexes=('date',),
        )


class SubscriptionEvent(object):
    @classmethod
    def to_entity(cls, properties, name=None, parent=None):
        return to_entity(
            'SubscriptionEvent',
            properties,
            name=name,
            parent=parent,
            include_in_indexes=('date',),
        )

    @classmethod
    def hash_name(cls, *args):
        if len(args) == 0:
            raise TypeError("Expected non-zero-length hash_name args")
        hash_string = '-'.join([str(arg) for arg in args])
        return hashlib.sha1(hash_string.encode()).hexdigest()

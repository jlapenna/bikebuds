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

import sys

def to_message(cls, entity, convert_fn, *args, **kwargs):
    attributes = {}
    if (entity.key is not None):
        attributes['id'] = entity.key.id()
    for key in entity._properties:
        value = getattr(entity, key, None)
        if value is None:
            continue
        try:
            value = convert_fn(key, value, *args, **kwargs)
            if value is None:
                continue
            attributes[key] = value
        except Exception, e:
            msg = 'Unable to convert: %s (%s) -> %s' % (
                    key, value, sys.exc_info()[1])
            raise Exception, Exception(msg), sys.exc_info()[2]
    return cls(**attributes)

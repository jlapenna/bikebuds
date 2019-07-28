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


class ClientState(object):
    class Types(object):
        UNKNOWN = 'UNKNOWN'
        ANDROID = 'ANDROID'
        IOS = 'IOS'
        WEB = 'WEB'

    @classmethod
    def get(cls, name, parent=None):
        key = ds_util.client.key('ClientState', name, parent=parent)
        client_state = ds_util.client.get(key)
        if client_state:
            return client_state
        client_state = Entity(key)
        client_state['active'] = True
        client_state['created'] = datetime.datetime.now(datetime.timezone.utc)
        client_state['modified'] = datetime.datetime.now(datetime.timezone.utc)
        client_state['token'] = name
        client_state['type'] = 'UNKNOWN'
        ds_util.client.put(client_state)
        return client_state

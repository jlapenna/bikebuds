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

from google.cloud.datastore import Key

from shared import ds_util

NONE = "NONE"


class SlackBot(object):
    @classmethod
    def key(cls, name: str, parent: Key = None) -> Key:
        return ds_util.client.key('SlackBot', name, parent=parent)


class SlackInstaller(object):
    @classmethod
    def key(cls, name: str, parent: Key = None) -> Key:
        return ds_util.client.key('SlackInstaller', name, parent=parent)


class SlackWorkspace(object):
    @classmethod
    def key(
        cls, enterprise_id: str = None, team_id: str = None, parent: Key = None
    ) -> Key:
        e_id = enterprise_id or NONE
        t_id = team_id or NONE
        return ds_util.client.key('SlackWorkspace', f"{e_id}-{t_id}", parent=parent)

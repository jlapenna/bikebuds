# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools

from google.cloud.datastore import Client

from shared.config import config


# Datastore Client
client = Client(project=config.project_id)


def key_from_path(path):
    if not path:
        return None
    return client.key(
        *itertools.chain(
            *[(pair.get('kind'), pair.get('id', pair.get('name'))) for pair in path]
        )
    )

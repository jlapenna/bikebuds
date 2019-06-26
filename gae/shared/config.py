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

import json
import os


class _Config(object):
    def __init__(self):
        base_path = 'lib/env'
        if not os.path.exists(base_path):
            base_path = 'env/'
        base_config = json.load(open(os.path.join(base_path, 'config.json')))
        for key, value in base_config.items():
            setattr(self, key, value)

        self.origins = _devOrProd(
            [self.devserver_url, self.frontend_url, self.api_url, self.backend_url],
            [self.frontend_url, self.api_url, self.backend_url])

        self.fitbit_creds = json.load(open(os.path.join(base_path,
            'service_keys/fitbit.json')))
        self.strava_creds = json.load(open(os.path.join(base_path,
            'service_keys/strava.json')))
        self.withings_creds = json.load(open(os.path.join(base_path,
            'service_keys/withings.json')))


def _devOrProd(dev, prod):
    if os.getenv('GAE_ENV', '').startswith('standard'):
        return prod
    else:
        return dev


config = _Config()

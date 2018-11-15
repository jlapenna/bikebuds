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

class ProdConfig(object):
    def __init__(self):
        self.frontend_url = 'https://www.bikebuds.cc'
        self.api_url = 'https://api.bikebuds.cc'
        self.backend_url = 'https://backend.bikebuds.cc'
        self.origins = [self.api_url, self.frontend_url, self.backend_url]
        self.fitbit_creds = json.load(open('lib/service_keys/fitbit.json'))
        self.strava_creds = json.load(open('lib/service_keys/strava.json'))
        self.withings_creds = json.load(open('lib/service_keys/withings.json'))
        self.prod = True
        self.local = False


class LocalConfig(object):
    def __init__(self):
        self.frontend_url = 'http://localhost:8080'
        self.api_url = 'http://localhost:8081'
        self.backend_url = 'http://localhost:8082'
        self.origins = [self.api_url, self.frontend_url, self.backend_url]
        self.fitbit_creds = json.load(open('lib/service_keys/fitbit-local.json'))
        self.strava_creds = json.load(open('lib/service_keys/strava-local.json'))
        self.withings_creds = json.load(open('lib/service_keys/withings-local.json'))
        self.prod = False
        self.local = True


if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    config = ProdConfig()
else:
    config = LocalConfig()

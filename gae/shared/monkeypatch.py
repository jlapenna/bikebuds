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

import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

# Hide spurrious errors.
import warnings
import urllib3.contrib.appengine
warnings.filterwarnings('ignore', r'urllib3 is using URLFetch',
        urllib3.contrib.appengine.AppEnginePlatformWarning)
warnings.filterwarnings('ignore',
        'The oauth2client.contrib.multistore_file module has been deprecated')

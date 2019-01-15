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

# Hide innocuous errors.
import warnings
import urllib3.contrib.appengine
warnings.filterwarnings('ignore', r'urllib3 is using URLFetch',
        urllib3.contrib.appengine.AppEnginePlatformWarning)

# Hide spammy oauth2client warnings.
import logging
logging.getLogger('oauth2client.contrib.multistore_file').setLevel(logging.ERROR)

# Hide spammy stravalib debugging
import logging
logging.getLogger('stravalib.model.Activity').setLevel(logging.WARN)
logging.getLogger('stravalib.model.Athlete').setLevel(logging.WARN)
logging.getLogger('stravalib.model.Club').setLevel(logging.WARN)

# Ensure that the requests library uses urlfetch for its network base.
# https://cloud.google.com/appengine/docs/standard/python/issue-requests#Python_Quotas_and_limits
import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()

# Increase the request timeout, strava can take a while.
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(30)

# Firebase admin setup
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials

try:
    FIREBASE_ADMIN_CREDS = credentials.Certificate(
            'lib/service_keys/bikebuds-app-firebase-adminsdk-888ix-2dfafbb556.json')
    firebase_admin.initialize_app(FIREBASE_ADMIN_CREDS)
except IOError, e:
    logging.warn('Unable to find admin credentials for firebase. This is probably a bug.');

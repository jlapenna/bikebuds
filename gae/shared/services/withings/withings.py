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
import logging

from google.appengine.ext import ndb

from shared.datastore import services
from shared.datastore.measures import Measure, Series

import nokia


class Synchronizer(object):
    def sync(self, service):
        client = create_client(service)
        measures = client.get_measures(lastupdate=0, updatetime=0)

        @ndb.transactional
        def put_series():
            Series.entity_from_withings(service.key, measures).put()
        return put_series()


def create_client(service):
    def refresh_callback(new_credentials):
        service.update_credentials(new_credentials)
    return nokia.NokiaApi(service.get_credentials(),
            refresh_cb=refresh_callback)

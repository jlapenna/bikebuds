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
from shared.datastore.measures import Measure

import nokia


class Synchronizer(object):

    def sync(self, user_key, service, service_creds):
        client = create_client(user_key, service_creds)
        measures = client.get_measures(lastupdate=0, updatetime=0)

        @ndb.transactional
        def put_measures():
            for measure in measures:
                Measure.from_withings(service.key, measure).put()
        put_measures()
        return True


def create_client(user_key, service_creds):
    def refresh_callback(new_credentials):
        services.ServiceCredentials.update(user_key, 'withings', new_credentials)
    return nokia.NokiaApi(service_creds, refresh_cb=refresh_callback)

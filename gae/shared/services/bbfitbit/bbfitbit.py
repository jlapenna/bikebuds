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

import fitbit

from shared.config import config
from shared.datastore import services
from shared.datastore.measures import Measure, Series


class Worker(object):

    def __init__(self, service):
        self.service = service
        self.client = create_client(service)

    def sync(self):
        measures = self.client.time_series('body/weight', period='max')

        @ndb.transactional
        def put_series():
            Series.entity_from_fitbit_time_series(
                    self.service.key, measures['body-weight']).put()
        return put_series()


def create_client(service):
    def refresh_callback(new_credentials):
        service.update_credentials(new_credentials)
    return fitbit.Fitbit(
            config.fitbit_creds['client_id'],
            config.fitbit_creds['client_secret'],
            access_token=service.get_credentials().access_token,
            refresh_token=service.get_credentials().refresh_token,
            expires_at=service.get_credentials().expires_at,
            redirect_uri=get_redirect_uri('frontend'),
            refresh_cb=refresh_callback,
            system=fitbit.Fitbit.METRIC)


def get_redirect_uri(dest):
    return config.frontend_url + '/services/fitbit/redirect?dest=' + dest

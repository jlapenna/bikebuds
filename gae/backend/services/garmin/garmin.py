# Copyright 2020 Google LLC
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

from shared import ds_util
from shared.services.garmin import client as garmin_client
from shared.datastore.series import Series


class Worker(object):
    def __init__(self, service):
        self.service = service
        self.client = garmin_client.create(service)

    def sync(self):
        self.sync_user()
        self.sync_measures()

    def sync_user(self):
        logging.debug('sync_user: %s', self.client.profile)

    def sync_measures(self):
        end_date = datetime.datetime.now(tz=datetime.timezone.utc).date()
        start_date = end_date - datetime.timedelta(days=365)

        # stats = self.client.get_stats(end_date.isoformat())
        body_comp = self.client.get_body_comp(
            start_date.isoformat(), end_date.isoformat()
        )

        series = Series.to_entity(
            body_comp['dateWeightList'], self.service.key.name, parent=self.service.key
        )

        ds_util.client.put(series)

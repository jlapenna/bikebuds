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
import random
import time

import flask

from retrying import retry

from google.cloud.datastore.key import Key

from shared import ds_util
from shared import task_util
from shared import responses
from shared.datastore.series import Series
from shared.datastore.service import Service
from shared.exceptions import SyncException
from shared.services.garmin import client as garmin_client
from shared.services.trainerroad.client import (
    create_client as trainerroad_create_client,
)

import sync_helper


module = flask.Blueprint('xsync', __name__)


@module.route('/tasks/process_measure', methods=['POST'])
def process_measure():
    params = task_util.get_payload(flask.request)
    user_key = params['user_key']
    measure = params['measure']
    logging.info('ProcessMeasure: %s %s', user_key, measure)

    _withings_garmin(flask.request, user_key, measure)
    _withings_trainerroad(flask.request, user_key, measure)
    return responses.OK


def _withings_garmin(request, user_key, measure):
    params = task_util.get_payload(request)
    user_key = params['user_key']
    measure = params['measure']
    logging.info('ProcessMeasure: withings_garmin: %s %s', user_key, measure)

    garmin_service = Service.get('garmin', parent=user_key)
    if not Service.has_credentials(garmin_service, required_key='password'):
        logging.debug('ProcessMeasure: Garmin not connected')
        return responses.OK

    if not measure.get('weight'):
        logging.debug('ProcessMeasure: Skipping non-weight measure.')
        return responses.OK

    try:
        client = garmin_client.create(garmin_service)
        client.set_weight(measure['weight'], measure['date'])
    except Exception:
        logging.exception('ProcessMeasure: Failed: %s', measure)
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


def _withings_trainerroad(request, user_key, measure):
    params = task_util.get_payload(request)
    user_key = params['user_key']
    measure = params['measure']
    logging.info('ProcessMeasure: withings_trainerroad: %s %s', user_key, measure)

    trainerroad_service = Service.get('trainerroad', parent=user_key)
    if not Service.has_credentials(trainerroad_service, required_key='password'):
        logging.debug('ProcessMeasure: Trainerroad not connected')
        return responses.OK

    if not measure.get('weight'):
        logging.debug('ProcessMeasure: Skipping non-weight measure.')
        return responses.OK

    try:
        client = trainerroad_create_client(trainerroad_service)
        with client:
            client.weight = measure['weight']
    except Exception:
        logging.exception('ProcessMeasure: Failed: %s', measure)
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


@module.route('/tasks/process_backfill', methods=['POST'])
def tasks_process_backfill():
    params = task_util.get_payload(flask.request)
    source_key = params['source_key']
    dest_key = params['dest_key']
    start = params['start']
    end = params['end']
    logging.info('process_backfill: %s->%s', source_key, dest_key)

    try:
        sync_helper.do(
            BackfillWorker(source_key, dest_key, start, end), work_key=source_key
        )
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


class BackfillWorker(object):
    def __init__(
        self,
        source_key: Key,
        dest_key: Key,
        start: datetime.datetime,
        end: datetime.datetime,
    ):
        self.source_key = source_key
        self.dest_key = dest_key
        self.start = start
        self.end = end

    def sync(self):
        source = ds_util.client.get(self.source_key)
        dest = ds_util.client.get(self.dest_key)

        if not self._check_creds(source):
            raise Exception('Source does not have credentials: %s', source.key)
        if not self._check_creds(dest):
            raise Exception('Dest does not have credentials: %s', dest.key)

        series = Series.get(source.key)
        if not series['measures']:
            logging.debug('Source has no measures: %s', source.key)
            return
        measures = series['measures']
        del series

        measures = [m for m in filter(lambda m: self._isbackfillable(m), measures)]
        logging.debug('Syncing %s measures to %s', len(measures), dest.key.name)

        if dest.key.name == 'garmin':
            client = garmin_client.create(dest)
            # Shorten and maybe GC measures as we iterate
            while len(measures) > 0:
                measure = measures.pop(0)

                @retry(
                    wait_exponential_multiplier=1000 * 2,
                    wait_exponential_max=1000 * 60 * 30,
                )
                def _set_weight():
                    logging.debug('Setting weight for %s', measure['date'])
                    try:
                        client.set_weight(measure['weight'], measure['date'])
                        time.sleep(random.randint(1, 2))
                    except Exception:
                        logging.exception(
                            'Failed to set_weight for %s', measure['date']
                        )
                        raise

                _set_weight()
                del measure

    def _check_creds(self, service):
        return (
            service.key.name == 'garmin'
            and Service.has_credentials(service, required_key='password')
        ) or (Service.has_credentials(service))

    def _isbackfillable(self, measure):
        if not measure.get('weight'):
            return False
        if self.start and measure['date'] < self.start:
            return False
        if self.end and measure['date'] > self.end:
            return False
        return True

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

from shared import monkeypatch

import datetime
import logging
import sys

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from urllib3.exceptions import TimeoutError

import flask

import nokia

from shared.config import config
from shared import task_util
from shared.datastore.activities import Activity
from shared.datastore.admin import DatastoreState, SyncState
from shared.datastore.athletes import Athlete
from shared.datastore.clubs import Club
from shared.datastore.measures import Series
from shared.datastore.services import Service
from shared.services.withings import withings
from shared.services.bbfitbit import bbfitbit
from shared.services.strava import strava

# Flask setup
app = flask.Flask(__name__)


class SyncException(Exception):
    pass


def _do_cleanup(version, datastore_state, cleanup_fn):
    if config.is_dev or (datastore_state.version < version):
        logging.info(
                'Running cleanup: %s -> %s', datastore_state.version, version)
        cleanup_fn()
        logging.info(
                'Completed cleanup: %s -> %s', datastore_state.version, version)
        datastore_state.version = version
    datastore_state.put()


@app.route('/tasks/cleanup', methods=['GET'])
def cleanup():
    result = DatastoreState.query().fetch(1)
    if len(result) == 0:
        datastore_state = DatastoreState()
    else:
        datastore_state = result[0]

    # Eg.,
    #def cleanup():
    #    ndb.delete_multi(Activity.query().fetch(keys_only=True))
    #_do_cleanup(7, datastore_state, cleanup)
    def cleanup():
        services = Service.query(Service.credentials != None)
        for service in services:
            if service.key.id() == 'withings':
                w = withings.Worker(service)
                w.remove_subscriptions()
    _do_cleanup(9, datastore_state, cleanup)

    return 'OK', 200


@app.route('/tasks/sync', methods=['GET'])
def sync():
    services = [
            service for service in Service.query(
                Service.credentials != None,
                Service.sync_enabled == True,
                Service.syncing == False
                )]
    task_util.sync_services(services)
    return 'OK', 200


@app.route('/tasks/service_sync/<service_name>', methods=['GET', 'POST'])
def service_sync(service_name):
    state_key = ndb.Key(urlsafe=flask.request.values.get('state_key'))
    service = ndb.Key(urlsafe=flask.request.values.get('service_key')).get()
    user_key = service.key.parent()
    service_creds = service.get_credentials()
    if service_creds is None:
        logging.info('No creds: %s', service.key)
        return 'OK', 250

    if service_name == 'withings':
        _do(withings.Worker(service), work_key=service.key)
    elif service_name == 'fitbit':
        _do(bbfitbit.Worker(service), work_key=service.key)
    elif service_name == 'strava':
        _do(strava.Worker(service), work_key=service.key)

    task_util.maybe_finish_sync_services_and_queue_process(service, state_key)
    return 'OK', 200


@app.route('/tasks/process', methods=['GET', 'POST'])
def process():
    """Called after all services for all users have finished syncing."""
    _do(strava.ClubMembershipsProcessor(), work_key='all', method='process')
    return 'OK', 200


@app.route('/tasks/process_event', methods=['GET', 'POST'])
def process_event():
    event_key = ndb.Key(urlsafe=flask.request.values.get('event_key'))
    service = event_key.parent().get()
    service_name = service.key.id()
    if service_name == 'withings':
        _do(withings.EventsWorker(service), work_key=service.key)
    elif service_name == 'fitbit':
        pass
    elif service_name == 'strava':
        _do(strava.EventsWorker(service), work_key=service.key)
    return 'OK', 200


@app.route('/tasks/process_weight_trend', methods=['GET', 'POST'])
def process_weight_trend():
    service_key = ndb.Key(urlsafe=flask.request.values.get('service_key'))
    service = service_key.get()
    service_name = service.key.id()
    if service_name == 'withings':
        _do(withings.WeightTrendWorker(service), work_key=service.key)
    elif service_name == 'fitbit':
        pass
    elif service_name == 'strava':
        pass
    return 'OK', 200


def _do(worker, work_key=None, method='sync'):
    work_name = worker.__class__.__name__
    try:
        logging.info('Worker starting: %s/%s', work_name, work_key)
        getattr(worker, method)()  # Dynamically run the provided method.
        sync_successful = True
        logging.info('Worker completed: %s/%s', work_name, work_key)
        return 'OK', 200
    except TimeoutError, e:
        logging.debug('%s for %s/%s, Originally: %s',
                sys.exc_info()[0].__name__,
                work_name,
                work_key,
                sys.exc_info()[1]
                )
        return 'Sync Failed', 503
    except Exception, e:
        msg = '"%s" for %s/%s' % (
                sys.exc_info()[1],
                work_name,
                work_key,
                )
        raise SyncException, SyncException(msg), sys.exc_info()[2]

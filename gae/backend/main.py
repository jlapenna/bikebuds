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
from shared.datastore.admin import DatastoreState, SubscriptionEvent, SyncState
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
    if datastore_state.version < version:
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

    def cleanup():
        ndb.delete_multi(Series.query().fetch(keys_only=True))
        ndb.delete_multi(Athlete.query().fetch(keys_only=True))
        ndb.delete_multi(Club.query().fetch(keys_only=True))
    _do_cleanup(6, datastore_state, cleanup)

    def cleanup():
        ndb.delete_multi(Activity.query().fetch(keys_only=True))
    _do_cleanup(7, datastore_state, cleanup)

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
    state_key = ndb.Key(urlsafe=flask.request.values.get('state'))
    service = ndb.Key(urlsafe=flask.request.values.get('service')).get()
    user_key = service.key.parent()
    service_creds = service.get_credentials()

    if service_name == 'withings':
        _do_sync(service, service_creds, withings.Synchronizer())
    elif service_name == 'fitbit':
        _do_sync(service, service_creds, bbfitbit.Synchronizer())
    elif service_name == 'strava':
        _do_sync(service, service_creds, strava.AthleteSynchronizer())
        _do_sync(service, service_creds, strava.ActivitiesSynchronizer())
        _do_sync(service, service_creds, strava.ClubsSynchronizer())

    @ndb.transactional(xg=True)
    def transact():
        state = state_key.get()
        state.completed_tasks += 1
        state.put()

        service.syncing = False
        service.sync_successful = True
        service.put()

        logging.info('Incrementing completed tasks for %s', state.key)
        if state.completed_tasks == state.total_tasks:
            logging.info('Completed all pending tasks for %s', state.key)
            taskqueue.add(
                    url='/tasks/process',
                    target='backend',
                    params={
                        'state': state_key.urlsafe(),
                        },
                    transactional=True)
    transact()

    return 'OK', 200


def _do_sync(service, service_creds, synchronizer, check_creds=True):
    if check_creds and service_creds is None:
        logging.info('No creds: %s/%s', service.key, synchronizer)
        return 'OK', 250

    sync_name = synchronizer.__class__.__name__
    try:
        logging.info('Synchronizer starting: %s', sync_name)
        synchronizer.sync(service)
        sync_successful = True
        logging.info('Synchronizer completed: %s', sync_name)
        return 'OK', 200
    except TimeoutError, e:
        logging.debug('%s for %s/%s (creds: %s), Originally: %s',
                sys.exc_info()[0].__name__,
                service.key,
                sync_name,
                service.get_credentials(),
                sys.exc_info()[1]
                )
        msg = 'DeadlineExceeded for %s/%s' % (
                service.key.id(),
                sync_name
                )
        return 'Sync Failed', 503
    except Exception, e:
        logging.debug('%s for %s/%s (creds: %s), Originally: %s',
            sys.exc_info()[0].__name__,
            service.key,
            sync_name,
            service.get_credentials(),
            sys.exc_info()[1]
            )
        msg = '%s for %s/%s' % (
                sys.exc_info()[0].__name__,
                service.key.id(),
                sync_name)
        raise SyncException, SyncException(msg), sys.exc_info()[2]


@app.route('/tasks/process', methods=['GET', 'POST'])
def process():
    _do_process(strava.ClubsMembersProcessor())
    return 'OK', 200


@app.route('/tasks/process_events', methods=['GET', 'POST'])
def process_events():
    _do_process(strava.SubscriptionEventProcessor())
    return 'OK', 200


def _do_process(processor):
    processor_name = processor.__class__.__name__
    try:
        logging.info('Processor starting: %s', processor_name)
        processor.sync()
        logging.info('Processor completed: %s', processor_name)
    except TimeoutError, e:
        logging.debug('Unable to process: %s -> %s',
            processor_name,
            sys.exc_info()[1]
            )
        msg = 'DeadlineExceeded for: %s' % (
            processor_name,
            )
        raise SyncException(msg)
    except Exception, e:
        logging.debug('%s for %s, Originally: %s',
            sys.exc_info()[0].__name__,
            processor_name,
            sys.exc_info()[1]
            )
        msg = '%s for %s' % (
                sys.exc_info()[0].__name__,
                processor_name)
        raise SyncException, SyncException(msg), sys.exc_info()[2]

def _add_test_sub_events():
    athlete_entity = Athlete.get_by_id(35056021, keys_only=True)
    SubscriptionEvent(parent=athlete_entity.parent(),
            **{'aspect_type': 'create',
                'event_time': 1549151210,
                'object_id': 2120517766,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {}
                }).put()
    SubscriptionEvent(parent=athlete_entity.parent(),
            **{'aspect_type': 'update',
                'event_time': 1549151212,
                'object_id': 2120517766,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {'title': 'Updated Title'}
                }).put()
    SubscriptionEvent(parent=athlete_entity.parent(),
            **{'aspect_type': 'create',
                'event_time': 1549151211,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {}
                }).put()
    SubscriptionEvent(parent=athlete_entity.parent(),
            **{'aspect_type': 'update',
                'event_time': 1549151213,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {'title': 'Second Updated Title'}
                }).put()
    SubscriptionEvent(parent=athlete_entity.parent(),
            **{'aspect_type': 'delete',
                'event_time': 1549151214,
                'object_id': 2120517859,
                'object_type': 'activity',
                'owner_id': 35056021,
                'subscription_id': 133263,
                'updates': {}
                }).put()

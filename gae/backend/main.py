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

import flask

import nokia

from shared.config import config
from shared.datastore import services
from shared.datastore import users
from shared.datastore.admin import DatastoreState
from shared.datastore.measures import Measure
from shared.services.withings import withings
from shared.services.bbfitbit import bbfitbit
from shared.services.strava import strava

# Flask setup
app = flask.Flask(__name__)


class SyncException(Exception):
    pass


@app.route('/tasks/cleanup', methods=['GET'])
def cleanup():
    result = DatastoreState.query().fetch(1)
    if len(result) == 0:
        datastore_state = DatastoreState()
    else:
        datastore_state = result[0]

    if datastore_state.version < 1:
        ndb.delete_multi(Measure.query().fetch(keys_only=True))
        datastore_state.version = 1

    datastore_state.put()


@app.route('/tasks/sync', methods=['GET'])
def sync():
    user_services = services.Service.query(
            services.Service.sync_enabled == True,
            services.Service.syncing == False
            ).fetch()
    for service in user_services:
        user_key = service.key.parent()
        @ndb.transactional
        def submit_sync(user_key, service):
            service.syncing = True
            service.sync_date = datetime.datetime.now()
            service.sync_successful = None
            service.put()
            task = taskqueue.add(
                    url='/tasks/service_sync/' + service.key.id(),
                    target='backend',
                    params={
                        'user': user_key.urlsafe(),
                        'service': service.key.urlsafe()},
                    transactional=True)
        submit_sync(user_key, service)

    return 'OK', 200


@app.route('/tasks/service_sync/<service_name>', methods=['GET', 'POST'])
def service_sync(service_name):
    user_key = ndb.Key(urlsafe=flask.request.values.get('user'))
    service = ndb.Key(urlsafe=flask.request.values.get('service')).get()
    service_creds = service.get_credentials()

    if service_name == 'withings':
        synchronizer = withings.Synchronizer()
    elif service_name == 'fitbit':
        synchronizer = bbfitbit.Synchronizer()
    elif service_name == 'strava':
        synchronizer = strava.Synchronizer()

    sync_successful = False
    try:
        if service_creds is None:
            logging.info('No service creds for this sync: %s', str(service))
            return 'OK', 250
        elif synchronizer is None:
            logging.info('No synchronizer for this sync: %s', str(service))
            return 'OK', 251
        else:
            synchronizer.sync(service)
            return 'OK', 200
    except Exception, e:
        msg = 'Unable to sync: %s using %s -> %s' % (
                service, service.get_credentials(), sys.exc_info()[1])
        raise SyncException, SyncException(msg), sys.exc_info()[2]
    finally:
        @ndb.transactional
        def finish_sync():
            service.syncing = False
            service.sync_successful = sync_successful
            service.put()
        finish_sync()


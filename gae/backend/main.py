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

import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import flask

import nokia

from shared.config import config
from shared.datastore import services
from shared.datastore import users
from shared.services.withings import withings
from shared.services.bbfitbit import bbfitbit

# Flask setup
app = flask.Flask(__name__)


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
            service.syncing=True
            service.sync_date=datetime.datetime.now()
            service.sync_successful=None
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
    if service_name == 'strava':
        logging.info('Cannot sync: %s', service_name)
        return flask.make_response('OK', 200)

    user_key = ndb.Key(urlsafe=flask.request.values.get('user'))
    service = ndb.Key(urlsafe=flask.request.values.get('service')).get()
    service_creds = services.ServiceCredentials.get_key(service.key).get()

    if service_creds is None:
        logging.info('No service creds for this sync: %s', str(service))
        @ndb.transactional
        def finish_sync():
            service.syncing=False
            service.sync_successful=False
            service.put()
        finish_sync()
        return 'OK', 250

    if service_name == 'withings':
        synchronizer = withings.Synchronizer()
    elif service_name == 'fitbit':
        synchronizer = bbfitbit.Synchronizer()

    try:
        result = synchronizer.sync(user_key, service, service_creds)
        @ndb.transactional
        def finish_sync():
            service.syncing=False
            service.sync_successful=True
            service.put()
        finish_sync()
    except:
        @ndb.transactional
        def finish_sync():
            service.syncing=False
            service.sync_successful=False
            service.put()
        finish_sync()
        raise

    return 'OK', 200

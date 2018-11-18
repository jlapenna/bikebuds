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
from shared.datastore.withings import Measure

# Flask setup
app = flask.Flask(__name__)


@app.route('/tasks/sync', methods=['GET'])
def sync():
    all_users = users.User.query()
    for user in all_users:
        user_services = services.Service.query(ancestor=user.key).fetch()
        for service in user_services:
            if service.key.id() != 'withings':
                continue
            if service.syncing:
                continue
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
            submit_sync(user.key, service)

    return 'OK', 200


@app.route('/tasks/service_sync/withings', methods=['GET', 'POST'])
def service_sync_withings():
    user_key = ndb.Key(urlsafe=flask.request.values.get('user'))
    service = ndb.Key(urlsafe=flask.request.values.get('service')).get()
    service_creds = services.ServiceCredentials.get_key(service.key).get()

    client = create_withings_client(user_key, service_creds)
    measures = client.get_measures(lastupdate=0, updatetime=0)

    @ndb.transactional
    def put_measures():
        for measure in measures:
            Measure.to_measure(service.key, measure).put()
    put_measures()

    @ndb.transactional
    def finish_sync():
        service.syncing=False
        service.sync_successful=True
        service.put()
    finish_sync()

    return flask.make_response('OK', 200)


def create_withings_client(user_key, service_creds):
    def refresh_callback(new_credentials):
        services.ServiceCredentials.update(user_key, 'withings', new_credentials)
    return nokia.NokiaApi(service_creds, refresh_cb=refresh_callback)

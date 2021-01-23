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

import logging

import flask

from google.cloud.datastore.entity import Entity

from shared import ds_util
from shared import logging_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.service import Service
from shared.exceptions import SyncException

from services.bbfitbit import bbfitbit
from services.garmin import garmin
from services.google import google
from services.slack import slack
from services.strava import strava
from services.trainerroad import trainerroad
from services.withings import withings
from services.withings.weight_trend_notif import WeightTrendWorker
from xsync import xsync

import sync_helper

app = flask.Flask(__name__)
app.register_blueprint(xsync.module, url_prefix='/xsync')
app.register_blueprint(bbfitbit.module, url_prefix='/services/fitbit')
app.register_blueprint(garmin.module, url_prefix='/services/garmin')
app.register_blueprint(google.module, url_prefix='/services/google')
app.register_blueprint(strava.module, url_prefix='/services/strava')
app.register_blueprint(trainerroad.module, url_prefix='/services/trainerroad')
app.register_blueprint(withings.module, url_prefix='/services/withings')
app.register_blueprint(slack.module, url_prefix='/services/slack')

app.logger.setLevel(logging.DEBUG)
logging_util.debug_logging()
logging_util.silence_logs()


@app.route('/tasks/cleanup', methods=['GET'])
def cleanup_task():
    result = [r for r in ds_util.client.query(kind='DatastoreState').fetch()]
    if len(result) == 0:
        datastore_state = Entity(ds_util.client.key('DatastoreState'))
    else:
        datastore_state = result[0]

    def cleanup():
        logging.info('No-op cleanup')

    _do_cleanup(0, datastore_state, cleanup)

    return responses.OK


@app.route('/tasks/sync', methods=['GET'])
def sync_task():
    services_query = ds_util.client.query(kind='Service')
    services_query.add_filter('sync_enabled', '=', True)
    services_query.add_filter('syncing', '=', False)
    services = [
        service
        for service in services_query.fetch()
        if Service.has_credentials(service)
    ]
    task_util.sync_services(services)
    return responses.OK


@app.route('/tasks/process_weight_trend', methods=['POST'])
def process_weight_trend_task():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('WeightTrendEvent: %s', event.key)
    service_key = event.key.parent
    service = ds_util.client.get(service_key)

    if service is None:
        logging.error('WeightTrendEvent: No service: %s', event.key)
        return responses.OK_NO_SERVICE

    try:
        if service.key.name == 'withings':
            sync_helper.do(WeightTrendWorker(service, event), work_key=event.key)
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


def _do_cleanup(version, datastore_state, cleanup_fn):
    if config.is_dev or (datastore_state.version < version):
        logging.debug('Running cleanup: %s -> %s', datastore_state.version, version)
        cleanup_fn()
        logging.info('Completed cleanup: %s -> %s', datastore_state.version, version)
        datastore_state.version = version
    datastore_state.put()


@app.route('/unittest', methods=['POST'])
def unittest():
    return responses.OK


@app.before_request
def before():
    logging_util.before()


@app.after_request
def after(response):
    return logging_util.after(response)


if __name__ == '__main__':
    host, port = config.backend_url[7:].split(':')
    app.run(host='localhost', port=port, debug=True)

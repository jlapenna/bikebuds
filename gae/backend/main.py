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
import enum
import logging
import sys

from urllib3.exceptions import TimeoutError

import flask

from google.cloud.datastore.entity import Entity

from shared.config import config
from shared import auth_util
from shared import ds_util
from shared import logging_util
from shared import task_util

from shared.datastore.service import Service
from shared.datastore.user import User
from shared.responses import Responses

from services.bbfitbit import bbfitbit
from services.strava import strava
from services.withings.weight_trend_notif import WeightTrendWorker
from services.withings import withings

app = flask.Flask(__name__)

app.logger.setLevel(logging.DEBUG)
logging_util.debug_logging()
logging_util.silence_logs()


class SyncException(Exception):
    pass


@app.route('/tasks/cleanup', methods=['GET'])
def cleanup_task():
    result = [r for r in ds_util.client.query(kind='DatastoreState').fetch()]
    if len(result) == 0:
        datastore_state = Entity(ds_util.client.key('DatastoreState'))
    else:
        datastore_state = result[0]

    # Eg.,
    #def cleanup():
    #    ndb.delete_multi(Activity.query().fetch(keys_only=True))
    #_do_cleanup(7, datastore_state, cleanup)

    return Responses.OK


@app.route('/sync/<name>', methods=['POST'])
def sync_trigger(name):
    claims = auth_util.verify(flask.request)
    user = User.get(claims)

    task_result = task_util.sync_service(Service.get(name, parent=user.key))
    return Responses.OK


@app.route('/tasks/sync', methods=['GET'])
def sync_task():
    services_query = ds_util.client.query(kind='Service')
    services_query.add_filter('sync_enabled', '=', True)
    services_query.add_filter('syncing', '=', False)
    services = [service for service in services_query.fetch()
            if Service.has_credentials(service)]
    task_util.sync_services(services)
    return Responses.OK


@app.route('/tasks/sync/service/<service_name>', methods=['POST'])
def sync_service_task(service_name):
    params = task_util.get_payload(flask.request)
    state_key = params['state_key']
    service = ds_util.client.get(params['service_key'])
    user_key = service.key.parent

    logging.debug('Validating state key')
    if state_key is None:
        logging.warn('Invalid state_key. params: %s', params)
        return Responses.OK_INVALID_STATE_KEY

    logging.debug('Validating credentials')
    if not Service.has_credentials(service):
        logging.warn('No creds: %s', service.key)
        return Response.OK_NO_CREDENTIALS

    if service_name == 'withings':
        _do(withings.Worker(service), work_key=service.key)
    elif service_name == 'fitbit':
        _do(bbfitbit.Worker(service), work_key=service.key)
    elif service_name == 'strava':
        _do(strava.Worker(service), work_key=service.key)

    task_util.maybe_finish_sync_services(service, state_key)
    return Responses.OK


@app.route('/sync/club/<club_id>', methods=['POST'])
def sync_club_trigger(club_id):
    claims = auth_util.verify(flask.request)
    user = User.get(claims)

    task_result = task_util.sync_club(club_id)
    return Responses.OK


@app.route('/tasks/sync/club/<club_id>', methods=['POST'])
def sync_club_task(club_id):
    _do(strava.ClubWorker(club_id), work_key=club_id)
    return Responses.OK


@app.route('/tasks/process_event', methods=['POST'])
def process_event_task():
    params = task_util.get_payload(flask.request)

    event_key = params['event_key']
    logging.info('Processing Event: Key: %s', event_key)

    # First try to get the service using the event_key's service.
    # If this event is coming from an old subscription / secret url, which
    # embeds a service_key in it, then we might get these.
    service_key = event_key.parent
    service = ds_util.client.get(service_key)
    
    if service is None:
        logging.warning('Cannot process event %s, no service', event_key)
        return Responses.OK_NO_SERVICE
    
    if not Service.has_credentials(service):
        logging.warning('Cannot process event %s, no credentials', event_key)
        return Responses.OK_NO_CREDENTIALS

    if service_key.name == 'withings':
        _do(withings.EventsWorker(service), work_key=service.key)
    elif service_key.name == 'fitbit':
        pass
    elif service_key.name == 'strava':
        _do(strava.EventsWorker(service), work_key=service.key)
    return Responses.OK


@app.route('/tasks/process_weight_trend', methods=['POST'])
def process_weight_trend_task():
    params = task_util.get_payload(flask.request)
    service_key = params['service_key']
    service = ds_util.client.get(service_key)
    service_name = service.key.name
    if service_name == 'withings':
        _do(WeightTrendWorker(service), work_key=service_key)
    elif service_name == 'fitbit':
        pass
    elif service_name == 'strava':
        pass
    return Responses.OK


def _do(worker, work_key=None, method='sync'):
    work_name = worker.__class__.__name__
    try:
        logging.debug('Worker starting: %s/%s', work_name, work_key)
        getattr(worker, method)()  # Dynamically run the provided method.
        logging.info('Worker completed: %s/%s', work_name, work_key)
    except Exception as e:
        raise SyncException(
                'Worker failed: %s/%s' % (work_name, work_key)) from e


def _do_cleanup(version, datastore_state, cleanup_fn):
    if config.is_dev or (datastore_state.version < version):
        logging.debug(
                'Running cleanup: %s -> %s', datastore_state.version, version)
        cleanup_fn()
        logging.info(
                'Completed cleanup: %s -> %s', datastore_state.version, version)
        datastore_state.version = version
    datastore_state.put()


@app.route('/unittest', methods=['POST'])
def unittest():
    return Responses.OK


@app.before_request
def before():
    logging_util.before()


@app.after_request
def after(response):
    return logging_util.after(response)


if __name__ == '__main__':
    host, port = config.backend_url[7:].split(':')
    app.run(host='localhost', port=port, debug=True)

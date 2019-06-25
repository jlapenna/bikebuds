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
import sys

from urllib3.exceptions import TimeoutError

import flask

from google.cloud.datastore.entity import Entity

from shared.config import config
from shared import auth_util
from shared import ds_util
from shared import logging_util
from shared import stackdriver_util
from shared import task_util
from shared.datastore.service import Service
from shared.datastore.user import User

from services.bbfitbit import bbfitbit
from services.strava import strava
from services.withings.weight_trend_notif import WeightTrendWorker
from services.withings import withings

app = flask.Flask(__name__)

app.logger.setLevel(logging.DEBUG)
logging_util.debug_logging()
logging_util.silence_logs()

stackdriver_util.start()


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

    return 'OK', 200


@app.route('/sync/<name>', methods=['POST'])
def sync_trigger(name):
    claims = auth_util.verify(flask.request)
    user = User.get(claims)

    task_result = task_util.sync_service(Service.get(name, parent=user.key))
    return 'OK', 200


@app.route('/tasks/sync', methods=['GET'])
def sync_task():
    services_query = ds_util.client.query(kind='Service')
    services_query.add_filter('sync_enabled', '=', True)
    services_query.add_filter('syncing', '=', False)
    services = [service for service in services_query.fetch()
            if Service.has_credentials(service)]
    task_util.sync_services(services)
    return 'OK', 200


@app.route('/tasks/sync/service/<service_name>', methods=['GET', 'POST'])
def sync_service_task(service_name):
    params = task_util.get_payload(flask.request)
    state_key = params['state_key']
    service = ds_util.client.get(params['service_key'])
    user_key = service.key.parent

    logging.debug('Validating state key')
    if state_key is None:
        logging.warn('Invalid state_key. params: %s', params)
        return 'Invalid state_key', 503

    logging.debug('Validating credentials')
    if not Service.has_credentials(service):
        logging.warn('No creds: %s', service.key)
        return 'OK', 250

    if service_name == 'withings':
        _do(withings.Worker(service), work_key=service.key)
    elif service_name == 'fitbit':
        _do(bbfitbit.Worker(service), work_key=service.key)
    elif service_name == 'strava':
        _do(strava.Worker(service), work_key=service.key)

    task_util.maybe_finish_sync_services(service, state_key)
    return 'OK', 200


@app.route('/sync/club/<club_id>', methods=['POST'])
def sync_club_trigger(club_id):
    claims = auth_util.verify(flask.request)
    user = User.get(claims)

    task_result = task_util.sync_club(club_id)
    return 'OK', 200


@app.route('/tasks/sync/club/<club_id>', methods=['GET', 'POST'])
def sync_club_task(club_id):
    _do(strava.ClubWorker(club_id), work_key=club_id)
    return 'OK', 200


@app.route('/tasks/process_event', methods=['GET', 'POST'])
def process_event_task():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('Processing Event: Key: %s', event.key)

    service_key = event.key.parent
    user_key = service_key.parent
    user = ds_util.client.get(user_key)

    # First try to get the service using the event key's service.
    # If this event is coming from an old subscription / secret url, which
    # embeds a service_key in it, then we might get these.
    service = ds_util.client.get(service_key)
    if service is None:
        # The event & Service we received might no longer have a User associated
        # with it. (Old subscriptions?) In which case, we have to use the user &
        # service name in a "Series.get" lookup rather than directly using the key.
        service = Service.get(service_key.name, parent=user_key)
    
    if service is None:
        logging.warn('Cannot process event %s, no service', event.key)
        return 'OK', 200
    
    if not Service.has_credentials(service):
        logging.warn('Cannot process event %s, no credentials', event.key)
        return 'OK', 200

    if service_key.name == 'withings':
        ds_util.client.put(event)
        _do(withings.EventsWorker(service), work_key=service.key)
    elif service_key.name == 'fitbit':
        pass
    elif service_key.name == 'strava':
        ds_util.client.put(event)
        _do(strava.EventsWorker(service), work_key=service.key)
    return 'OK', 200


@app.route('/tasks/process_weight_trend', methods=['GET', 'POST'])
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
    return 'OK', 200


def _do(worker, work_key=None, method='sync'):
    work_name = worker.__class__.__name__
    try:
        logging.debug('Worker starting: %s/%s', work_name, work_key)
        getattr(worker, method)()  # Dynamically run the provided method.
        logging.info('Worker completed: %s/%s', work_name, work_key)
        return 'OK', 200
    except Exception as e:
        raise SyncException(
                'Worker failed: %s/%s' % (work_name, work_key)) from e
        return 'Sync Failed', 503


def _do_cleanup(version, datastore_state, cleanup_fn):
    if config.is_dev or (datastore_state.version < version):
        logging.debug(
                'Running cleanup: %s -> %s', datastore_state.version, version)
        cleanup_fn()
        logging.info(
                'Completed cleanup: %s -> %s', datastore_state.version, version)
        datastore_state.version = version
    datastore_state.put()


@app.route('/unittest', methods=['GET', 'POST'])
def unittest():
    return 'OK', 200


@app.before_request
def before():
    logging_util.before()


@app.after_request
def after(response):
    return logging_util.after(response)


if __name__ == '__main__':
    host, port = config.backend_url[7:].split(':')
    app.run(host='localhost', port=port, debug=True)

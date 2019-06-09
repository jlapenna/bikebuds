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
from shared import task_util
from shared.datastore.service import Service
from shared.datastore.user import User

from services.bbfitbit import bbfitbit
from services.strava import strava
from services.withings import withings

logging_util.silence_logs()

app = flask.Flask(__name__)


class SyncException(Exception):
    pass


@app.route('/test', methods=['POST'])
def test_trigger():
    claims = auth_util.verify(flask.request)
    user = User.get(claims)

    e = Entity(ds_util.client.key('Task'))
    e.update({'param1': 'value1'})
    e['param2'] = 'value2'

    task_result = task_util.test(e)
    logging.debug('Enqueued Task: %s', task_result)
    return 'OK', 200


@app.route('/tasks/test', methods=['POST'])
def test_task():
    entity = task_util.get_payload(flask.request)
    logging.info('/tasks/test: %s', entity)
    return 'OK', 200


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
def cleanup_task():
    result = ds_util.client.query(kind='DatastoreState').fetch()
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
    services_query.add_filter('credentials', '!=', None)
    services_query.add_filter('sync_enabled', '==', True)
    services_query.add_filter('syncing', '==', False)
    services = [service for service in services_query.fetch()]
    task_util.sync_services(services)
    return 'OK', 200


@app.route('/tasks/service_sync/<service_name>', methods=['GET', 'POST'])
def service_sync_task(service_name):
    logging.warn('Starting service_sync')
    params = task_util.get_payload(flask.request)
    state_key = params['state_key']
    service = ds_util.client.get(params['service_key'])
    user_key = service.key.parent

    logging.warn('Validating state key')
    if state_key is None:
        logging.info('Invalid state_key. params: %s', params)
        return 'Invalid state_key', 503

    logging.warn('Validating credentials')
    if service['credentials'] is None:
        logging.info('No creds: %s', service.key)
        return 'OK', 250

    if service_name == 'withings':
        _do(withings.Worker(service), work_key=service.key)
    elif service_name == 'fitbit':
        _do(bbfitbit.Worker(service), work_key=service.key)
    elif service_name == 'strava':
        logging.warn('doing work')
        _do(strava.Worker(service), work_key=service.key)

    logging.warn('Finishing work')
    task_util.maybe_finish_sync_services_and_queue_process(service, state_key)
    logging.warn('Finished work')
    return 'OK', 200


@app.route('/tasks/process', methods=['GET', 'POST'])
def process_task():
    """Called after all services for all users have finished syncing."""
    _do(strava.ClubMembershipsProcessor(), work_key='all', method='process')
    return 'OK', 200


@app.route('/tasks/process_event', methods=['GET', 'POST'])
def process_event_task():
    params = task_util.get_payload(flask.request)
    event = params['event']
    service = ds_util.client.get(event.key.parent)
    service_name = service.key.name
    
    if service['credentials'] is None:
        logging.warn('Cannot process event %s, no credentials', event_key)
        return 'OK', 200

    if service_name == 'withings':
        _do(withings.EventsWorker(service), work_key=service.key)
    elif service_name == 'fitbit':
        pass
    elif service_name == 'strava':
        # TODO: refactor to do this inline.
        ds_util.client.put(event)
        _do(strava.EventsWorker(service), work_key=service.key)
    return 'OK', 200


@app.route('/tasks/process_weight_trend', methods=['GET', 'POST'])
def process_weight_trend_task():
    params = task_util.get_payload(flask.request)
    service_key = params['service_key']
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
    except TimeoutError as e:
        logging.debug('%s for %s/%s, Originally: %s',
                sys.exc_info()[0].__name__,
                work_name,
                work_key,
                sys.exc_info()[1]
                )
        return 'Sync Failed', 503
    except Exception as e:
        msg = '"%s" for %s/%s' % (
                sys.exc_info()[1],
                work_name,
                work_key,
                )
        raise SyncException(msg).with_traceback(sys.exc_info()[2])


@app.before_request
def before():
    logging_util.before()


@app.after_request
def after(response):
    return logging_util.after(response)


logging_util.debug_logging()
if __name__ == '__main__':
    host, port = config.backend_url[7:].split(':')
    app.run(host='localhost', port=port, debug=True)
else:
    # When run under dev_appserver it is not '__main__'.
    pass

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
from shared.datastore.bot import Bot
from shared.datastore.service import Service
from shared.exceptions import SyncException
from shared.services.garmin import client as garmin_client
from shared.services.strava.club_worker import ClubWorker as StravaClubWorker

from backfill.backfill import BackfillWorker
from services.bbfitbit import bbfitbit
from services.google import google
from services.garmin import garmin
from services.slack import slack
from services.strava import strava
from services.strava.events_worker import EventsWorker as StravaEventsWorker
from services.withings import withings
from services.withings.withings import EventsWorker as WithingsEventsWorker
from services.withings.weight_trend_notif import WeightTrendWorker

import sync_helper

app = flask.Flask(__name__)
app.register_blueprint(google.module, url_prefix='/services/google')
app.register_blueprint(garmin.module, url_prefix='/services/garmin')

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


@app.route('/tasks/sync/service/<service_name>', methods=['POST'])
def sync_service_task(service_name):
    logging.debug('Syncing: %s', service_name)
    params = task_util.get_payload(flask.request)

    service = ds_util.client.get(params['service_key'])
    if not (
        (
            service_name == 'garmin'
            and Service.has_credentials(service, required_key='password')
        )
        or (Service.has_credentials(service))
    ):
        logging.warn('No creds: %s', service.key)
        Service.set_sync_finished(service, error='No credentials')
        return responses.OK_NO_CREDENTIALS

    try:
        Service.set_sync_started(service)
        if service_name == 'withings':
            sync_helper.do(withings.Worker(service), work_key=service.key)
        elif service_name == 'fitbit':
            sync_helper.do(bbfitbit.Worker(service), work_key=service.key)
        elif service_name == 'strava':
            sync_helper.do(strava.Worker(service), work_key=service.key)
        elif service_name == 'garmin':
            sync_helper.do(garmin.Worker(service), work_key=service.key)
        elif service_name == 'google':
            sync_helper.do(google.Worker(service), work_key=service.key)
        Service.set_sync_finished(service)
        return responses.OK
    except SyncException as e:
        Service.set_sync_finished(service, error=str(e))
        return responses.OK_SYNC_EXCEPTION


@app.route('/tasks/sync/club/<club_id>', methods=['GET', 'POST'])
def sync_club(club_id):
    logging.debug('Syncing: %s', club_id)
    service = Service.get('strava', parent=Bot.key())
    sync_helper.do(StravaClubWorker(club_id, service), work_key=service.key)
    return responses.OK


@app.route('/tasks/process_event', methods=['POST'])
def process_event_task():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('Event: %s', event.key)

    # First try to get the service using the event.key's service.
    # If this event is coming from an old subscription / secret url, which
    # embeds a service_key in it, then we might get these.
    service_key = event.key.parent
    service = ds_util.client.get(service_key)

    if service is None:
        logging.error('Event: No service: %s', event.key)
        return responses.OK_NO_SERVICE

    if not Service.has_credentials(service):
        logging.warning('Event: No credentials: %s', event.key)
        return responses.OK_NO_CREDENTIALS

    try:
        if service_key.name == 'withings':
            sync_helper.do(WithingsEventsWorker(service, event), work_key=event.key)
        elif service_key.name == 'strava':
            sync_helper.do(StravaEventsWorker(service, event), work_key=event.key)
    except SyncException:
        return responses.OK_SYNC_EXCEPTION
    return responses.OK


@app.route('/tasks/process_slack_event', methods=['POST'])
def process_slack_event_task():
    params = task_util.get_payload(flask.request)
    event = params['event']
    logging.info('SlackEvent: %s', event.key)
    return slack.process_slack_event(event)


@app.route('/tasks/process_measure', methods=['POST'])
def process_measure():
    params = task_util.get_payload(flask.request)
    user_key = params['user_key']
    measure = params['measure']
    logging.info('ProcessMeasure: %s', measure)

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


@app.route('/tasks/process_backfill', methods=['POST'])
def process_backfill_task():
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

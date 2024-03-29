# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import flask

from flask_restx import Resource, Namespace, fields

import stravalib

from shared import auth_util
from shared import ds_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.club import Club
from shared.datastore.service import Service
from shared.services.strava.club_worker import ClubWorker as StravaClubWorker
from shared.services.withings.client import create_client as withings_create_client

from models import (
    EntityModel,
    club_entity_model,
    key_model,
    service_entity_model,
    service_model,
    sync_model,
    user_entity_model,
    WrapEntity,
)

api = Namespace('admin', 'Bikebuds Admin API')


auth_url_model = api.model('AuthUrl', {'auth_url': fields.String})

user_state_model = api.model(
    'UserState',
    {
        'user': fields.Nested(user_entity_model, skip_none=True),
        'google': fields.Nested(service_model, skip_none=True),
        'strava': fields.Nested(service_model, skip_none=True),
        'withings': fields.Nested(service_model, skip_none=True),
        'fitbit': fields.Nested(service_model, skip_none=True),
    },
)

slack_workspace_model = api.model('SlackWorkspace', {})
slack_workspace_entity_model = EntityModel(slack_workspace_model)

slack_model = api.model(
    'Slack',
    {
        'service': fields.Nested(service_entity_model, skip_none=True),
        'workspaces': fields.Nested(slack_workspace_entity_model),
        'installers': fields.Wildcard(fields.String),
        'bots': fields.Wildcard(fields.String),
    },
)


@api.route('/strava_auth_url')
class StravaAuthUrl(Resource):
    @api.doc('get_strava_auth_url')
    @api.marshal_with(auth_url_model, skip_none=True)
    def get(self):
        auth_util.get_bot(flask.request)
        redirect_uri = config.frontend_url + '/services/strava/echo'

        client = stravalib.client.Client()
        url = client.authorization_url(
            client_id=config.strava_creds['client_id'],
            redirect_uri=redirect_uri,
            approval_prompt='force',
            scope=['activity:read_all', 'profile:read_all'],
        )
        return {'auth_url': url}


@api.route('/process_events')
class ProcessEventsResource(Resource):
    def get(self):
        auth_util.get_bot(flask.request)

        sub_events_query = ds_util.client.query(kind='SubscriptionEvent')
        for sub_event in sub_events_query.fetch():
            task_util.process_event(sub_event.key)
        return responses.OK


@api.route('/subscription/remove')
class RemoveSubscriptionResource(Resource):
    @api.doc('remove_subscription')
    def post(self):
        auth_util.get_bot(flask.request)

        callbackurl = flask.request.form.get('callbackurl', None)
        logging.info('Unsubscribing: %s', callbackurl)

        if callbackurl is None or 'withings' not in callbackurl:
            return responses.BAD_REQUEST

        services_query = ds_util.client.query(kind='Service')
        services_query.add_filter('sync_enabled', '=', True)
        services = [
            service
            for service in services_query.fetch()
            if service.key.name == 'withings' and service.get('credentials') is not None
        ]

        for service in services:
            logging.info('Unsubscribing: %s from %s', callbackurl, service.key)
            client = withings_create_client(service)
            results = []
            try:
                result = client.unsubscribe(callbackurl)
                logging.info(
                    'Unsubscribed %s from %s (%s)', callbackurl, service.key, result
                )
                results.append(
                    {
                        'callbackurl': callbackurl,
                        'result': str(result),
                        'service': str(service.key),
                    }
                )
            except Exception as e:
                logging.exception(
                    'Unable to unsubscribe %s from %s', callbackurl, service.key
                )
                results.append(
                    {
                        'callbackurl': callbackurl,
                        'error': str(e),
                        'service': str(service.key),
                    }
                )
        return results


@api.route('/clubs')
class GetClubsResource(Resource):
    @api.doc('get_clubs')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self):
        bot = auth_util.get_bot(flask.request)

        service = Service.get('strava', parent=bot.key)
        club_query = ds_util.client.query(kind='Club', ancestor=service.key)

        return [WrapEntity(club) for club in club_query.fetch()]


@api.route('/users')
class GetUsersResource(Resource):
    @api.doc('get_users')
    @api.marshal_with(user_state_model, skip_none=True)
    def get(self):
        bot = auth_util.get_bot(flask.request)

        user_entities = [bot]
        user_entities += ds_util.client.query(kind='User').fetch()
        users = []
        for user_entity in user_entities:
            users.append(
                {
                    'user': WrapEntity(user_entity),
                    'google': Service.get('google', parent=user_entity.key),
                    'strava': Service.get('strava', parent=user_entity.key),
                    'withings': Service.get('withings', parent=user_entity.key),
                    'fitbit': Service.get('fitbit', parent=user_entity.key),
                }
            )

        return users


@api.route('/delete')
class DeleteResource(Resource):
    @api.doc('delete', body=key_model)
    @api.marshal_with(key_model, skip_none=True)
    def post(self):
        auth_util.get_bot(flask.request)

        key = ds_util.key_from_path(api.payload.get('path'))
        if key is None or ds_util.client.get(key) is None:
            logging.debug('No entity with key: %s', key)
            return key
        children_query = ds_util.client.query(ancestor=key)
        children_query.keys_only()
        ds_util.client.delete_multi(child.key for child in children_query.fetch())

        return key


@api.route('/sync/club/<club_id>')
class SyncClubResource(Resource):
    @api.doc('sync_club')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self, club_id):
        bot = auth_util.get_bot(flask.request)

        service = Service.get('strava', parent=bot.key)
        club = StravaClubWorker(club_id, service).sync()

        return WrapEntity(club)


@api.route('/club/track/<club_id>')
class ClubTrackResource(Resource):
    @api.doc('track_club')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self, club_id):
        bot = auth_util.get_bot(flask.request)

        service = Service.get('strava', parent=bot.key)
        club = StravaClubWorker(club_id, service).sync_club()

        return WrapEntity(club)


@api.route('/club/untrack/<club_id>')
class ClubUntrackResource(Resource):
    @api.doc('untrack_club')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self, club_id):
        bot = auth_util.get_bot(flask.request)

        service = Service.get('strava', parent=bot.key)
        club = Club.get(club_id, parent=service.key)
        if club is not None:
            ds_util.client.delete(club.key)

        return None


@api.route('/slack')
class SlackResource(Resource):
    @api.doc('get_slack')
    @api.marshal_with(slack_model, skip_none=True)
    def get(self):
        bot = auth_util.get_bot(flask.request)
        service = Service.get('slack', parent=bot.key)
        query = ds_util.client.query(kind='SlackWorkspace', ancestor=service.key)
        workspaces = [e for e in query.fetch()]
        return {'service': WrapEntity(service), 'workspaces': workspaces}


@api.route('/service/<name>')
class ServiceResource(Resource):
    @api.doc('get_admin_service')
    @api.marshal_with(service_entity_model, skip_none=True)
    def get(self, name):
        bot = auth_util.get_bot(flask.request)

        service = Service.get(name, parent=bot.key)
        return WrapEntity(service)


@api.route('/sync/<name>')
class SyncResource(Resource):
    @api.doc('sync_admin_service', body=sync_model)
    @api.marshal_with(service_entity_model, skip_none=True)
    def post(self, name):
        bot = auth_util.get_bot(flask.request)

        force = api.payload.get('force', False)
        service = Service.get(name, parent=bot.key)
        task_util.sync_service(service, force=force)
        return WrapEntity(service)

    def get(self, name):
        bot = auth_util.get_bot(flask.request)

        service = Service.get(name, parent=bot.key)
        task_util.sync_service(service, force=True)
        return responses.OK


@api.route('/admin_disconnect/<name>')
class ServiceDisconnect(Resource):
    @api.doc('admin_disconnect')
    @api.marshal_with(service_entity_model, skip_none=True)
    def post(self, name):
        bot = auth_util.get_bot(flask.request)

        service = Service.get(name, parent=bot.key)
        Service.clear_credentials(service)
        ds_util.client.put(service)
        return WrapEntity(service)

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

from flask_restplus import Resource, Namespace, fields

import stravalib

from shared import auth_util
from shared import ds_util
from shared import responses
from shared import task_util
from shared.config import config
from shared.datastore.bot import Bot
from shared.datastore.club import Club
from shared.datastore.service import Service
from shared.services.strava.club_worker import ClubWorker as StravaClubWorker
from shared.services.withings.client import create_client as withings_create_client

from models import (
    club_entity_model,
    service_entity_model,
    WrapEntity,
)

api = Namespace('admin', 'Bikebuds Admin API')


auth_url_model = api.model('AuthUrl', {'auth_url': fields.String})


bot_model = api.model(
    'Bot', {'strava': fields.Nested(service_entity_model, skip_none=True)}
)


@api.route('/bot')
class BotResource(Resource):
    @api.doc('get_bot')
    @api.marshal_with(bot_model, skip_none=True)
    def get(self):
        auth_util.verify_admin(flask.request)
        user = Bot.get()
        strava = Service.get('strava', parent=user.key)
        return {'strava': WrapEntity(strava)}


@api.route('/strava_auth_url')
class StravaAuthUrl(Resource):
    @api.doc('get_strava_auth_url')
    @api.marshal_with(auth_url_model, skip_none=True)
    def get(self):
        auth_util.verify_admin(flask.request)
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
        auth_util.verify_admin(flask.request)

        sub_events_query = ds_util.client.query(kind='SubscriptionEvent')
        for sub_event in sub_events_query.fetch():
            task_util.process_event(sub_event.key)
        return responses.OK


@api.route('/subscription/remove')
class RemoveSubscriptionResource(Resource):
    @api.doc('remove_subscription')
    def post(self):
        auth_util.verify_admin(flask.request)

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
        auth_util.verify_admin(flask.request)

        service = Service.get('strava', parent=Bot.key())
        club_query = ds_util.client.query(kind='Club', ancestor=service.key)

        return [WrapEntity(club) for club in club_query.fetch()]


@api.route('/sync/club/<club_id>')
class SyncClubResource(Resource):
    @api.doc('sync_club')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self, club_id):
        auth_util.verify_admin(flask.request)

        service = Service.get('strava', parent=Bot.key())
        club = StravaClubWorker(club_id, service).sync()

        return WrapEntity(club)


@api.route('/club/track/<club_id>')
class ClubTrackResource(Resource):
    @api.doc('track_club')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self, club_id):
        auth_util.verify_admin(flask.request)

        service = Service.get('strava', parent=Bot.key())
        club = StravaClubWorker(club_id, service).sync_club()

        return WrapEntity(club)


@api.route('/club/untrack/<club_id>')
class ClubUntrackResource(Resource):
    @api.doc('untrack_club')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self, club_id):
        auth_util.verify_admin(flask.request)

        service = Service.get('strava', parent=Bot.key())
        club = Club.get(club_id, parent=service.key)
        if club is not None:
            ds_util.client.delete(club.key)

        return None

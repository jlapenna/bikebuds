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


import datetime

import flask
from flask_restx import Namespace, Resource


from shared import auth_util
from shared import ds_util
from shared import task_util

from shared.datastore.athlete import Athlete
from shared.datastore.bot import Bot
from shared.datastore.client_state import ClientState
from shared.datastore.club import Club
from shared.datastore.user import User
from shared.datastore.service import Service
from shared.datastore.series import Series

from models import (
    activity_entity_model,
    auth_model,
    client_state_entity_model,
    client_state_model,
    club_entity_model,
    filter_parser,
    get_arg,
    preferences_model,
    profile_model,
    route_entity_model,
    segment_entity_model,
    segments_parser,
    series_entity_model,
    service_entity_model,
    WrapEntity,
)


api = Namespace('bikebuds', 'Bikebuds API')


@api.route('/activities')
class ActivitiesResource(Resource):
    @api.doc('get_activities')
    @api.marshal_with(activity_entity_model, skip_none=True, as_list=True)
    def get(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        service = Service.get('strava', parent=user.key)
        activities_query = ds_util.client.query(
            kind='Activity', ancestor=service.key, order=['-start_date']
        )
        one_year_ago = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(days=365)
        activities_query.add_filter('start_date', '>', one_year_ago)
        return [WrapEntity(a) for a in activities_query.fetch(limit=20)]


@api.route('/clients')
class ClientsResource(Resource):
    @api.doc('get_clients')
    @api.marshal_with(client_state_entity_model, skip_none=True, as_list=True)
    def get(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        clients_query = ds_util.client.query(
            kind='ClientState', ancestor=user.key, order=['-modified']
        )
        return [WrapEntity(c) for c in clients_query.fetch()]


@api.route('/client/<client_id>')
class ClientResource(Resource):
    @api.doc('get_client')
    @api.marshal_with(client_state_entity_model, skip_none=True)
    def get(self, client_id):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        return WrapEntity(ClientState.get(client_id, parent=user.key))


@api.route('/update_client')
class UpdateClientResource(Resource):
    @api.doc('update_client', body=client_state_model)
    @api.marshal_with(client_state_entity_model, skip_none=True)
    def post(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        new_client = api.payload
        existing_client = ClientState.get(new_client['token'], parent=user.key)
        existing_client.update(new_client)
        existing_client['modified'] = datetime.datetime.now(datetime.timezone.utc)
        ds_util.client.put(existing_client)
        return WrapEntity(existing_client)


@api.route('/club/<club_id>')
class ClubResource(Resource):
    @api.doc('get_club')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self, club_id):
        club_id = int(club_id)
        auth_util.verify(flask.request)

        bot_strava = Service.get('strava', parent=Bot.key())
        club = Club.get(club_id, parent=bot_strava.key)

        # Find the user's club reference.
        if club is None:
            flask.abort(404)

        return WrapEntity(club)


@api.route('/club/<club_id>/activities')
class ClubActivitiesResource(Resource):
    @api.doc('get_club_activities')
    @api.marshal_with(activity_entity_model, skip_none=True, as_list=True)
    def get(self, club_id):
        club_id = int(club_id)
        auth_util.verify(flask.request)

        bot_strava = Service.get('strava', parent=Bot.key())
        club = Club.get(club_id, parent=bot_strava.key)

        # Find the user's club reference.
        if club is None:
            flask.abort(404)

        activities_query = ds_util.client.query(kind='Activity', ancestor=club.key)
        all_activities = [a for a in activities_query.fetch()]

        return [WrapEntity(a) for a in all_activities]


@api.route('/preferences')
class PreferencesResource(Resource):
    @api.doc('update_preferences', body=preferences_model)
    @api.marshal_with(preferences_model, skip_none=True)
    def post(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        user['preferences'].update(api.payload)
        ds_util.client.put(user)
        return user['preferences']


@api.route('/profile')
class ProfileResource(Resource):
    @api.doc('get_profile')
    @api.marshal_with(profile_model, skip_none=True)
    def get(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        strava = Service.get('strava', parent=user.key)
        strava_connected = Service.has_credentials(strava)
        athlete = Athlete.get_private(strava.key)

        return dict(
            user=WrapEntity(user),
            athlete=WrapEntity(athlete),
            signup_complete=strava_connected,
        )


@api.route('/routes')
class RoutesResource(Resource):
    @api.doc('get_routes')
    @api.marshal_with(route_entity_model, skip_none=True, as_list=True)
    def get(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        service = Service.get('strava', parent=user.key)
        routes_query = ds_util.client.query(
            kind='Route', ancestor=service.key, order=['-id']
        )
        routes = [WrapEntity(a) for a in routes_query.fetch()]
        return routes


@api.route('/segments')
class SegmentsResource(Resource):
    @api.doc('get_segments')
    @api.marshal_with(segment_entity_model, skip_none=True, as_list=True)
    def get(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        service = Service.get('strava', parent=user.key)
        segments_query = ds_util.client.query(
            kind='Segment', ancestor=service.key, order=['-id']
        )
        segments = [WrapEntity(a) for a in segments_query.fetch()]
        return segments


@api.route('/segments/compare')
@api.expect(segments_parser)
class SegmentsCompareResource(Resource):
    @api.doc('compare_segments')
    @api.marshal_with(segment_entity_model, skip_none=True, as_list=True)
    def get(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        service = Service.get('strava', parent=user.key)
        segments_arg = get_arg('segments')
        segments = []
        for segment_id in segments_arg:
            entity = ds_util.client.get(
                ds_util.client.key('Segment', segment_id, parent=service.key)
            )
            segments.append(WrapEntity(entity))
        return segments


@api.route('/series')
@api.expect(filter_parser)
class SeriesResource(Resource):
    @api.doc('get_series')
    @api.marshal_with(series_entity_model, skip_none=True)
    def get(self):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        service_name = user['preferences']['weight_service'].lower()
        series = Series.get(
            service_name, ds_util.client.key('Service', service_name, parent=user.key)
        )
        if series is None:
            return WrapEntity(None)

        filter_arg = get_arg('filter')
        if filter_arg:
            series['measures'] = [m for m in series['measures'] if filter_arg in m]
        return WrapEntity(series)


@api.route('/service/<name>')
class ServiceResource(Resource):
    @api.doc('get_service')
    @api.marshal_with(service_entity_model, skip_none=True)
    def get(self, name):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        service = Service.get(name, parent=user.key)
        return WrapEntity(service)

    @api.doc('update_service', body=service_entity_model)
    @api.marshal_with(service_entity_model, skip_none=True)
    def post(self, name):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        new_service = api.payload
        existing_service = Service.get(name, parent=user.key)
        existing_service.update(new_service)
        ds_util.client.put(existing_service)
        return WrapEntity(existing_service)


@api.route('/disconnect/<name>')
class ServiceDisconnect(Resource):
    @api.doc('disconnect')
    @api.marshal_with(service_entity_model, skip_none=True)
    def get(self, name):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)
        service = Service.get(name, parent=user.key)
        Service.clear_credentials(service)
        ds_util.client.put(service)
        return WrapEntity(service)


@api.route('/sync/<name>')
class SyncResource(Resource):
    @api.doc('sync_service')
    @api.marshal_with(service_entity_model, skip_none=True)
    def get(self, name):
        claims = auth_util.verify(flask.request)
        user = User.get(claims)

        service = Service.get(name, parent=user.key)
        task_util.sync_service(service)

        return WrapEntity(service)


@api.route('/auth')
class AuthResource(Resource):
    @api.doc('auth')
    @api.marshal_with(auth_model, skip_none=True)
    def get(self):
        claims = auth_util.verify(flask.request)
        custom_token = auth_util.create_custom_token(claims)
        return {'token': custom_token.decode('utf-8')}


@api.route('/unittest')
class UnittestResource(Resource):
    def get(self):
        return None

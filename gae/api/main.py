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
import logging

import flask
from flask import Flask
from flask_cors import CORS
from flask_restplus import Api, Resource, fields

from google.cloud.datastore.entity import Entity
from google.cloud.datastore import helpers

from shared import auth_util
from shared import ds_util
from shared import logging_util
from shared import stackdriver_util
from shared import task_util
from shared.config import config
from flask_cors import cross_origin

from shared.datastore.athlete import Athlete
from shared.datastore.client_state import ClientState
from shared.datastore.club import Club
from shared.datastore.user import User
from shared.datastore.service import Service
from shared.datastore.series import Series

stackdriver_util.start()

app = Flask(__name__)
CORS(app, origins=config.origins)

app.logger.setLevel(logging.DEBUG)
logging_util.debug_logging()
logging_util.silence_logs()

# https://flask-restplus.readthedocs.io/en/stable/swagger.html#documenting-authorizations
# https://cloud.google.com/endpoints/docs/openapi/authenticating-users-firebase#configuring_your_openapi_document
authorizations = {
    'api_key': {
        'name': 'key',
        'in': 'query',
        'type': 'apiKey',
    },
    'firebase': {
        'authorizationUrl': '',
        'flow': 'implicit',
        'type': 'oauth2',
        'x-google-issuer': 'https://securetoken.google.com/' + config.project_id,
        'x-google-jwks_uri': 'https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com'
    }
}
api = Api(app, version='1.0', title='Bikebuds API',
    description='A Bikebuds API',
    security=list(authorizations.keys()),
    authorizations=authorizations,
    default='bikebuds'
)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_OPERATION_ID = True


def WrapEntity(entity):
    if entity is None:
        return None
    return {'key': entity.key, 'properties': entity}


def EntityModel(nested_model):
    return api.model(nested_model.name + 'Entity', {
        'key': fields.Nested(key_model),
        'properties': fields.Nested(nested_model)
    })


class CredentialsField(fields.Raw):
    def format(self, value):
        return 'credentials' is not None


class DateTimeNaive(fields.DateTime):
    def parse(self, value):
       parsed_value = super().parse(value)
       if parsed_value is not None:
           parsed_value = parsed_value.replace(tzinfo=None)
       return parsed_value


key_model = api.model('EntityKey', {
    'path': fields.Raw,
})


service_model = api.model('Service', {
    'credentials': CredentialsField(default=False),
    'sync_date': fields.DateTime,
    'sync_enabled': fields.Boolean(default=False),
    'sync_successful': fields.Boolean(default=False),
})
service_entity_model = EntityModel(service_model)

measure_model = api.model('Measure', {
    #'body_temperature': fields.Float,
    #'bone_mass': fields.Float,
    'date': fields.DateTime,
    #'diastolic_blood_pressure': fields.Integer,
    #'fat_free_mass': fields.Float,
    #'fat_mass_weight': fields.Float,
    'fat_ratio': fields.Float,
    #'heart_pulse': fields.Integer,
    #'height': fields.Float,
    #'hydration': fields.Float,
    #'muscle_mass': fields.Float,
    #'pulse_wave_velocity': fields.Float,
    #'skin_temperature': fields.Float,
    #'spo2': fields.Float,
    #'systolic_blood_pressure': fields.Integer,
    #'temperature': fields.Float,
    'weight': fields.Float,
})

series_model = api.model('Series', {
    'measures': fields.List(
        fields.Nested(measure_model, skip_none=True), default=tuple())
})
series_entity_model = EntityModel(series_model)

geo_point_model = api.model('GeoPoint', {
    'latitude': fields.String,
    'longitude': fields.String,
    })

map_model = api.model('PolylineMap', {
    'id': fields.String,
    #'polyline': fields.String,
    'summary_polyline': fields.String,
    })

member_model = api.model('Member', {
    'firstname': fields.String,
    'lastname': fields.String,
    'profile_medium': fields.String,
})

club_model = api.model('Club', {
    #'admin' : fields.Boolean,
    'city' : fields.String,
    #'club_type' : fields.String,
    #'country' : fields.String,
    #'cover_photo' : fields.String,
    'cover_photo_small' : fields.String,
    'description' : fields.String,
    #'featured' : fields.Boolean,
    'id' : fields.Integer,
    #'member_count' : fields.Integer,
    'members' : fields.List(fields.Nested(member_model, skip_none=True), default=tuple()),
    #'membership' : fields.String,
    'name' : fields.String,
    #'owner' : fields.Boolean,
    #'private' : fields.Boolean,
    #'profile' : fields.String,
    'profile_medium' : fields.String,
    #'sport_type' : fields.String,
    #'state' : fields.String,
    'url' : fields.String,
})
club_entity_model = EntityModel(club_model)

athlete_model = api.model('Athlete', {
    #'admin': fields.String,
    #'agreed_to_terms': fields.String,
    #'approve_followers': fields.String,
    #'athlete_type': fields.String,
    #'badge_type_id': fields.String,
    #'bikes': fields.String,
    'city': fields.String,
    'clubs': fields.List(fields.Nested(club_model, skip_none=True)),
    #'country': fields.String,
    #'created_at': fields.String,
    #'date_preference': fields.String,
    #'dateofbirth': fields.String,
    #'description': fields.String,
    #'email': fields.String,
    #'email_facebook_twitter_friend_joins': fields.String,
    #'email_kom_lost': fields.String,
    #'email_language': fields.String,
    #'email_send_follower_notices': fields.String,
    #'facebook_sharing_enabled': fields.String,
    'firstname': fields.String,
    #'follower': fields.String,
    #'follower_count': fields.String,
    #'follower_request_count': fields.String,
    #'friend': fields.String,
    #'friend_count': fields.String,
    #'ftp': fields.String,
    #'global_privacy': fields.String,
    'id': fields.Integer,
    #'instagram_username': fields.String,
    'lastname': fields.String,
    #'max_heartrate': fields.String,
    #'measurement_preference': fields.String,
    #'membership': fields.String,
    #'mutual_friend_count': fields.String,
    #'offer_in_app_payment': fields.String,
    #'owner': fields.String,
    #'plan': fields.String,
    #'premium': fields.Boolean,
    #'premium_expiration_date': fields.String,
    #'profile': fields.String,
    'profile_medium': fields.String,
    #'profile_original': fields.String,
    #'receive_comment_emails': fields.String,
    #'receive_follower_feed_emails': fields.String,
    #'receive_kudos_emails': fields.String,
    #'receive_newsletter': fields.String,
    #'sample_race_distance': fields.String,
    #'sample_race_time': fields.String,
    #'sex': fields.String,
    #'shoes': fields.String,
    #'state': fields.String,
    #'subscription_permissions': fields.String,
    #'super_user': fields.String,
    #'updated_at': fields.String,
    #'username': fields.String,
    #'weight': fields.String,
})
athlete_entity_model = EntityModel(athlete_model)

activity_model = api.model('Activity', {
    #'achievement_count': fields.Integer,
    'athlete': fields.Nested(athlete_model, skip_none=True),
    #'athlete_count': fields.Integer,
    #'average_cadence': fields.Float,
    #'average_heartrate': fields.String,
    'average_speed': fields.Float,
    #'average_temp': fields.Integer,
    #'average_watts': fields.Float,
    #'calories': fields.String,
    #'comment_count': fields.Integer,
    #'commute': fields.Boolean,
    #'description': fields.String,
    #'device_name': fields.String,
    #'device_watts': fields.Boolean,
    'distance': fields.Float,
    #'elapsed_time': fields.Integer,
    #'embed_token': fields.String,
    'end_latlng': fields.Nested(geo_point_model, skip_none=True),
    #'external_id': fields.String,
    #'flagged': fields.Boolean,
    #'from_accepted_tag': fields.Boolean,
    #'gear': fields.String,
    #'gear_id': fields.String,
    #'guid': fields.String,
    #'has_heartrate': fields.Boolean,
    #'has_kudoed': fields.Boolean,
    #'highlighted_kudosers': fields.String,
    'id': fields.Integer,
    #'instagram_primary_photo': fields.String,
    'kilojoules': fields.Float,
    #'kudos_count': fields.Integer,
    #'laps': fields.String,
    #'location_city': fields.String,
    #'location_state': fields.String,
    #'manual': fields.Boolean,
    'map': fields.Nested(map_model, skip_none=True),
    #'max_speed': fields.Float,
    #'max_watts': fields.String,
    'moving_time': fields.Integer,
    'name': fields.String,
    #'partner_brand_tag': fields.String,
    #'partner_logo_url': fields.String,
    #'photo_count': fields.Integer,
    #'photos': fields.String,
    #'pr_count': fields.Integer,
    #'segment_efforts': fields.String,
    #'segment_leaderboard_opt_out': fields.String,
    #'splits_metric': fields.String,
    #'splits_standard': fields.String,
    'start_date':  fields.DateTime,
    'start_date_local': DateTimeNaive,
    'start_latlng': fields.Nested(geo_point_model, skip_none=True),
    #'suffer_score': fields.String,
    #'timezone': fields.String,
    #'total_elevation_gain': fields.Float,
    #'total_photo_count': fields.Integer,
    #'trainer': fields.String,
    #'type': fields.String,
    #'upload_id': fields.String,
    #'utc_offset': fields.Integer,
    #'weighted_average_watts': fields.String,
    #'workout_type': fields.String,
})
activity_entity_model = EntityModel(activity_model)

preferences_model = api.model('Preferences', {
    'daily_weight_notif': fields.Boolean,
    'units': fields.String,
    'weight_service': fields.String,
})

user_model = api.model('User', {
    'admin': fields.Boolean(default=False),
    'preferences': fields.Nested(preferences_model, skip_none=True),
})
user_entity_model = EntityModel(user_model)

profile_model = api.model('Profile', {
    'athlete': fields.Nested(athlete_entity_model, skip_none=True),
    'signup_complete': fields.Boolean(default=False),
    'user': fields.Nested(user_entity_model, skip_none=True),
})

client_state_model = api.model('ClientState', {
    'active': fields.Boolean,
    'token': fields.String,
    'type': fields.String,
})
client_state_entity_model = EntityModel(client_state_model)


@api.route('/activities')
class ActivitiesResource(Resource):
    @api.doc('get_activities')
    @api.marshal_with(activity_entity_model, skip_none=True, as_list=True)
    def get(self):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        service = Service.get('strava', parent=user.key)
        activities_query = ds_util.client.query(
                kind='Activity', ancestor=service.key, order=['-start_date'])
        one_year_ago = (datetime.datetime.now(datetime.timezone.utc) -
                datetime.timedelta(days=365))
        activities_query.add_filter('start_date', '>', one_year_ago)
        activities = [WrapEntity(a) for a in activities_query.fetch()]
        return activities


@api.route('/client/<client_id>')
class ClientResource(Resource):
    @api.doc('get_client')
    @api.marshal_with(client_state_entity_model, skip_none=True)
    def get(self, client_id):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        return WrapEntity(ClientState.get(client_id, parent=user.key))


@api.route('/update_client')
class ClientResource(Resource):
    @api.doc('update_client', body=client_state_model)
    @api.marshal_with(client_state_entity_model, skip_none=True)
    def post(self):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        new_client = api.payload
        existing_client = ClientState.get(new_client['token'], parent=user.key)
        existing_client.update(new_client)
        existing_client['modified'] = datetime.datetime.now(
                datetime.timezone.utc)
        ds_util.client.put(existing_client)
        return WrapEntity(existing_client)


@api.route('/club/<club_id>')
class ClubResource(Resource):
    @api.doc('get_club')
    @api.marshal_with(club_entity_model, skip_none=True)
    def get(self, club_id):
        club_id = int(club_id)
        claims = auth_util.verify_claims(flask.request)

        user = User.get(claims)
        strava = Service.get('strava', parent=user.key)
        athlete = Athlete.get_private(strava.key)
        if athlete is None:
            flask.abort(500)

        # Find the user's club reference.
        club = Club.get(club_id, parent=strava.key)
        if club is None:
            flask.abort(404)

        athlete_query = ds_util.client.query(kind='Athlete',
                order=['firstname', 'lastname'])
        athlete_query.add_filter('clubs.id', '=', club_id)
        club['members'] = [a for a in athlete_query.fetch()]

        return WrapEntity(club)


@api.route('/club/<club_id>/activities')
class ClubActivitiesResource(Resource):
    @api.doc('get_club_activities')
    @api.marshal_with(activity_entity_model, skip_none=True, as_list=True)
    def get(self, club_id):
        club_id = int(club_id)
        claims = auth_util.verify_claims(flask.request)

        user = User.get(claims)
        strava = Service.get('strava', parent=user.key)
        athlete = Athlete.get_private(strava.key)
        if athlete is None:
            flask.abort(500)

        club = Club.get(club_id, parent=strava.key)
        if club is None:
            flask.abort(404)

        # Find all their activities in the past two weeks.
        two_weeks = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)
        activities_query = ds_util.client.query(kind='Activity')
        activities_query.add_filter('start_date', '>', two_weeks)
        activities_query.add_filter('clubs', '=', club_id)
        all_activities = [a for a in activities_query.fetch()]

        return [WrapEntity(a) for a in sorted(all_activities,
                key=lambda value: value['start_date'],
                reverse=True)]


@api.route('/user')
class UserResource(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_entity_model, skip_none=True)
    def get(self):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        return WrapEntity(user)


@api.route('/preferences')
class PreferencesResource(Resource):
    @api.doc('update_preferences', body=preferences_model)
    @api.marshal_with(preferences_model, skip_none=True)
    def post(self):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        user['preferences'].update(api.payload)
        ds_util.client.put(user)
        return user['preferences']


@api.route('/profile')
class ProfileResource(Resource):
    @api.doc('get_profile')
    @api.marshal_with(profile_model, skip_none=True)
    def get(self):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        strava = Service.get('strava', parent=user.key)
        strava_connected = Service.has_credentials(strava)
        athlete = Athlete.get_private(strava.key)

        return dict(
                user=WrapEntity(user),
                athlete=WrapEntity(athlete),
                signup_complete=strava_connected
                )


@api.route('/series')
class SeriesResource(Resource):
    @api.doc('get_series')
    @api.marshal_with(series_entity_model, skip_none=True)
    def get(self):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        service_name = user['preferences']['weight_service'].lower()
        series = Series.get(service_name,
                ds_util.client.key('Service', service_name, parent=user.key))
        return WrapEntity(series)


@api.route('/service/<name>')
class ServiceResource(Resource):
    @api.doc('get_service')
    @api.marshal_with(service_entity_model, skip_none=True)
    def get(self, name):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        service = Service.get(name, parent=user.key)
        return WrapEntity(service)

    @api.doc('update_service', body=service_entity_model)
    @api.marshal_with(service_entity_model, skip_none=True)
    def post(self, name):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        new_service = api.payload
        existing_service = Service.get(name, parent=user.key)
        existing_service.update(new_service)
        ds_util.client.put(existing_service)
        return WrapEntity(existing_service)


@api.route('/sync/<name>')
class SyncResource(Resource):
    @api.doc('sync_service')
    @api.marshal_with(service_entity_model, skip_none=True)
    def get(self, name):
        claims = auth_util.verify_claims(flask.request)
        user = User.get(claims)
        service = Service.get(name, parent=user.key)

        task_result = task_util.sync_service(service)
        return WrapEntity(service)


@api.route('/unittest')
class UnittestResource(Resource):
    def get(self):
        return None


@app.route('/_ah/warmup')
def warmup():
    return '', 200, {}


@app.before_request
def before():
    logging_util.before()


@app.after_request
def after(response):
    return logging_util.after(response)


if __name__ == '__main__':
    host, port = config.api_url[7:].split(':')
    app.run(host='localhost', port=port, debug=True)

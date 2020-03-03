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

from flask_restx import Namespace, fields, reqparse


api = Namespace('models')


def WrapEntity(entity):
    if entity is None:
        return None
    return {'key': entity.key, 'properties': entity}


def EntityModel(nested_model):
    return api.model(
        nested_model.name + 'Entity',
        {'key': fields.Nested(key_model), 'properties': fields.Nested(nested_model)},
    )


class CredentialsField(fields.Raw):
    def format(self, value):
        return value is not None


class DateTimeNaive(fields.DateTime):
    def parse(self, value):
        parsed_value = super().parse(value)
        if parsed_value is not None:
            parsed_value = parsed_value.replace(tzinfo=None)
        return parsed_value


key_model = api.model('EntityKey', {'path': fields.Raw})


sync_state_model = api.model(
    'SyncState',
    {
        'syncing': fields.Boolean(default=False),
        'successful': fields.Boolean(default=False),
        'error': fields.String,
        'enqueued_at': fields.DateTime,
        'started_at': fields.DateTime,
        'updated_at': fields.DateTime,
    },
)


service_model = api.model(
    'Service',
    {
        'credentials': CredentialsField(default=False),
        'sync_enabled': fields.Boolean(default=False),
        'sync_state': fields.Nested(sync_state_model),
    },
)
service_entity_model = EntityModel(service_model)

measure_model = api.model(
    'Measure',
    {
        # 'body_temperature': fields.Float,
        # 'bone_mass': fields.Float,
        'date': fields.DateTime,
        # 'diastolic_blood_pressure': fields.Integer,
        # 'fat_free_mass': fields.Float,
        # 'fat_mass_weight': fields.Float,
        'fat_ratio': fields.Float,
        # 'heart_pulse': fields.Integer,
        # 'height': fields.Float,
        # 'hydration': fields.Float,
        # 'muscle_mass': fields.Float,
        # 'pulse_wave_velocity': fields.Float,
        # 'skin_temperature': fields.Float,
        # 'spo2': fields.Float,
        # 'systolic_blood_pressure': fields.Integer,
        # 'temperature': fields.Float,
        'weight': fields.Float,
        'weight_error': fields.List(fields.Float),
    },
)

series_model = api.model(
    'Series',
    {
        'measures': fields.List(
            fields.Nested(measure_model, skip_none=True), default=tuple()
        )
    },
)
series_entity_model = EntityModel(series_model)

geo_point_model = api.model(
    'GeoPoint', {'latitude': fields.String, 'longitude': fields.String,}
)

elevation_point_model = api.model(
    'ElevationPoint',
    {
        'location': fields.Nested(geo_point_model),
        'elevation': fields.Float,
        'resolution': fields.Float,
    },
)

map_model = api.model(
    'PolylineMap',
    {
        'id': fields.String,
        'polyline': fields.String,
        'summary_polyline': fields.String,
    },
)

member_model = api.model(
    'Member',
    {
        'firstname': fields.String,
        'lastname': fields.String,
        'profile_medium': fields.String,
    },
)

club_model = api.model(
    'Club',
    {
        # 'admin' : fields.Boolean,
        'city': fields.String,
        # 'club_type' : fields.String,
        # 'country' : fields.String,
        # 'cover_photo' : fields.String,
        'cover_photo_small': fields.String,
        'description': fields.String,
        # 'featured' : fields.Boolean,
        'id': fields.Integer,
        # 'member_count' : fields.Integer,
        'members': fields.List(
            fields.Nested(member_model, skip_none=True), default=tuple()
        ),
        # 'membership' : fields.String,
        'name': fields.String,
        # 'owner' : fields.Boolean,
        # 'private' : fields.Boolean,
        # 'profile' : fields.String,
        'profile_medium': fields.String,
        # 'sport_type' : fields.String,
        # 'state' : fields.String,
        'url': fields.String,
    },
)
club_entity_model = EntityModel(club_model)

athlete_model = api.model(
    'Athlete',
    {
        # 'admin': fields.String,
        # 'agreed_to_terms': fields.String,
        # 'approve_followers': fields.String,
        # 'athlete_type': fields.String,
        # 'badge_type_id': fields.String,
        # 'bikes': fields.String,
        'city': fields.String,
        'clubs': fields.List(fields.Nested(club_model, skip_none=True)),
        # 'country': fields.String,
        # 'created_at': fields.String,
        # 'date_preference': fields.String,
        # 'dateofbirth': fields.String,
        # 'description': fields.String,
        # 'email': fields.String,
        # 'email_facebook_twitter_friend_joins': fields.String,
        # 'email_kom_lost': fields.String,
        # 'email_language': fields.String,
        # 'email_send_follower_notices': fields.String,
        # 'facebook_sharing_enabled': fields.String,
        'firstname': fields.String,
        # 'follower': fields.String,
        # 'follower_count': fields.String,
        # 'follower_request_count': fields.String,
        # 'friend': fields.String,
        # 'friend_count': fields.String,
        # 'ftp': fields.String,
        # 'global_privacy': fields.String,
        'id': fields.Integer,
        # 'instagram_username': fields.String,
        'lastname': fields.String,
        # 'max_heartrate': fields.String,
        # 'measurement_preference': fields.String,
        # 'membership': fields.String,
        # 'mutual_friend_count': fields.String,
        # 'offer_in_app_payment': fields.String,
        # 'owner': fields.String,
        # 'plan': fields.String,
        # 'premium': fields.Boolean,
        # 'premium_expiration_date': fields.String,
        # 'profile': fields.String,
        'profile_medium': fields.String,
        # 'profile_original': fields.String,
        # 'receive_comment_emails': fields.String,
        # 'receive_follower_feed_emails': fields.String,
        # 'receive_kudos_emails': fields.String,
        # 'receive_newsletter': fields.String,
        # 'sample_race_distance': fields.String,
        # 'sample_race_time': fields.String,
        # 'sex': fields.String,
        # 'shoes': fields.String,
        # 'state': fields.String,
        # 'subscription_permissions': fields.String,
        # 'super_user': fields.String,
        # 'updated_at': fields.String,
        # 'username': fields.String,
        # 'weight': fields.String,
    },
)
athlete_entity_model = EntityModel(athlete_model)

photos_primary_model = api.model(
    'PhotosPrimary',
    {
        'id': fields.Integer,
        'source': fields.String,
        'unique_id': fields.String,
        'urls': fields.String,
    },
)

photos_summary_model = api.model(
    'PhotosSummary',
    {
        'count': fields.Integer,
        'primary': fields.Nested(photos_primary_model, skip_none=True),
    },
)

activity_model = api.model(
    'Activity',
    {
        # 'achievement_count': fields.Integer,
        'athlete': fields.Nested(athlete_model, skip_none=True),
        # 'athlete_count': fields.Integer,
        # 'average_cadence': fields.Float,
        # 'average_heartrate': fields.String,
        'average_speed': fields.Float,
        # 'average_temp': fields.Integer,
        # 'average_watts': fields.Float,
        # 'calories': fields.String,
        # 'comment_count': fields.Integer,
        # 'commute': fields.Boolean,
        # 'description': fields.String,
        # 'device_name': fields.String,
        # 'device_watts': fields.Boolean,
        'distance': fields.Float,
        # 'elapsed_time': fields.Integer,
        # 'embed_token': fields.String,
        'end_latlng': fields.Nested(geo_point_model, skip_none=True),
        # 'external_id': fields.String,
        # 'flagged': fields.Boolean,
        # 'from_accepted_tag': fields.Boolean,
        # 'gear': fields.String,
        # 'gear_id': fields.String,
        # 'guid': fields.String,
        # 'has_heartrate': fields.Boolean,
        # 'has_kudoed': fields.Boolean,
        # 'highlighted_kudosers': fields.String,
        'id': fields.Integer,
        # 'instagram_primary_photo': fields.String,
        'kilojoules': fields.Float,
        # 'kudos_count': fields.Integer,
        # 'laps': fields.String,
        # 'location_city': fields.String,
        # 'location_state': fields.String,
        # 'manual': fields.Boolean,
        'map': fields.Nested(map_model, skip_none=True),
        # 'max_speed': fields.Float,
        # 'max_watts': fields.String,
        'moving_time': fields.Integer,
        'name': fields.String,
        # 'partner_brand_tag': fields.String,
        # 'partner_logo_url': fields.String,
        # 'photo_count': fields.Integer,
        'photos': fields.Nested(photos_summary_model, skip_none=True),
        # 'pr_count': fields.Integer,
        # 'segment_efforts': fields.String,
        # 'segment_leaderboard_opt_out': fields.String,
        # 'splits_metric': fields.String,
        # 'splits_standard': fields.String,
        'start_date': fields.DateTime,
        'start_date_local': DateTimeNaive,
        'start_latlng': fields.Nested(geo_point_model, skip_none=True),
        # 'suffer_score': fields.String,
        # 'timezone': fields.String,
        # 'total_elevation_gain': fields.Float,
        # 'total_photo_count': fields.Integer,
        # 'trainer': fields.String,
        # 'type': fields.String,
        # 'upload_id': fields.String,
        # 'utc_offset': fields.Integer,
        # 'weighted_average_watts': fields.String,
        # 'workout_type': fields.String,
    },
)
activity_entity_model = EntityModel(activity_model)

preferences_model = api.model(
    'Preferences',
    {
        'daily_weight_notif': fields.Boolean,
        'units': fields.String,
        'weight_service': fields.String,
    },
)

user_model = api.model(
    'User', {'preferences': fields.Nested(preferences_model, skip_none=True),},
)
user_entity_model = EntityModel(user_model)

profile_model = api.model(
    'Profile',
    {
        'athlete': fields.Nested(athlete_entity_model, skip_none=True),
        'signup_complete': fields.Boolean(default=False),
        'user': fields.Nested(user_entity_model, skip_none=True),
    },
)

client_state_model = api.model(
    'ClientState',
    {
        'active': fields.Boolean,
        'created': fields.DateTime,
        'modified': fields.DateTime,
        'token': fields.String,
        'type': fields.String,
    },
)
client_state_entity_model = EntityModel(client_state_model)

route_model = api.model(
    'Route',
    {
        'id': fields.Integer,
        'athlete': fields.Nested(athlete_model, skip_none=True),
        'description': fields.String,
        'distance': fields.Float,
        'elevation_gain': fields.Float,
        'map': fields.Nested(map_model, skip_none=True),
        'name': fields.String,
        'private': fields.Boolean,
        'starred': fields.Boolean,
        'sub_type': fields.String,
        'timestamp': fields.DateTime,
        'type': fields.String,
    },
)
route_entity_model = EntityModel(route_model)

segment_model = api.model(
    'Segment',
    {
        'id': fields.Integer,
        'name': fields.String,
        'activity_type': fields.String,
        'distance': fields.Float,
        'average_grade': fields.Float,
        'maximum_grade': fields.Float,
        'elevation_high': fields.Float,
        'elevation_low': fields.Float,
        'start_latlng': fields.Nested(geo_point_model, skip_none=True),
        'end_latlng': fields.Nested(geo_point_model, skip_none=True),
        'start_latitude': fields.Float,
        'end_latitude': fields.Float,
        'start_longitude': fields.Float,
        'end_longitude': fields.Float,
        'climb_category': fields.Integer,
        'city': fields.String,
        'state': fields.String,
        'country': fields.String,
        'private': fields.Boolean,
        'starred': fields.Boolean,
        # 'athlete_segment_stats': EntityAttribute(AthleteSegmentStats, (DETAILED,)) #: Undocumented attrib holding stats for current athlete.
        # detailed attribs
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime,
        'total_elevation_gain': fields.Float,
        'map': fields.Nested(map_model, skip_none=True),
        'effort_count': fields.Integer,
        'athlete_count': fields.Integer,
        'hazardous': fields.Boolean,
        'star_count': fields.Integer,
        'pr_time': fields.Integer,
        'starred_date': fields.DateTime,
        # 'athlete_pr_effort': EntityAttribute(AthletePrEffort, (DETAILED,))
        'elevations': fields.List(fields.Nested(elevation_point_model, skip_none=True)),
    },
)
segment_entity_model = EntityModel(segment_model)


auth_model = api.model('Auth', {'token': fields.String})
auth_entity_model = EntityModel(auth_model)


filter_parser = reqparse.RequestParser()
filter_parser.add_argument(
    'filter', location='args', help='A filter for measures in a series.'
)


segments_parser = reqparse.RequestParser()
segments_parser.add_argument(
    'segments',
    action='split',
    type=int,
    help='Sequence of segments to compare',
    location='args',
)


def get_arg(name):
    parser_name = name + '_parser'
    arg_parser = globals()[parser_name]
    try:
        args = arg_parser.parse_args()
        return args[name]
    except Exception:
        logging.exception('Failed to parse %s, skipping %s.' % (name, name))
        return None

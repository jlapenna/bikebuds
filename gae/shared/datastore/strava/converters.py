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

"""Converts stravalib objects into Entities."""

import datetime
import pytz

from google.cloud.datastore.entity import Entity
from google.cloud.datastore.helpers import GeoPoint
from sortedcontainers import SortedSet

from shared import ds_util
from shared.hash_util import hash_name


class _ActivityConverter(object):
    __ALL_FIELDS = SortedSet(
        [
            'achievement_count',
            'activity_hash',
            'athlete',
            'athlete_count',
            'average_cadence',
            'average_heartrate',
            'average_speed',
            'average_temp',
            'average_watts',
            'best_efforts',
            'calories',
            'comment_count',
            'commute',
            'description',
            'device_name',
            'device_watts',
            'distance',
            'elapsed_time',
            'elev_high',
            'elev_low',
            'embed_token',
            'end_latlng',
            'external_id',
            'flagged',
            'from_accepted_tag',
            'gear',
            'gear_id',
            'guid',
            'has_heartrate',
            'has_kudoed',
            'highlighted_kudosers',
            'id',
            'instagram_primary_photo',
            'kilojoules',
            'kudos_count',
            'laps',
            'location_city',
            'location_country',
            'location_state',
            'manual',
            'map',
            'max_heartrate',
            'max_speed',
            'max_watts',
            'moving_time',
            'name',
            'partner_brand_tag',
            'partner_logo_url',
            'photo_count',
            'photos',
            'pr_count',
            'private',
            'segment_efforts',
            'segment_leaderboard_opt_out',
            'splits_metric',
            'splits_standard',
            'start_date',
            'start_date_local',
            'start_latitude',
            'start_latlng',
            'start_longitude',
            'suffer_score',
            'timezone',
            'total_elevation_gain',
            'total_photo_count',
            'trainer',
            'type',
            'upload_id',
            'utc_offset',
            'weighted_average_watts',
            'workout_type',
        ]
    )
    __INCLUDE_IN_INDEXES = SortedSet(['id', 'start_date'])
    __STORED_FIELDS = SortedSet(
        [
            'athlete',
            'average_speed',
            'distance',
            'end_latlng',
            'firstanme',
            'kilojoules',
            'lastname',
            'moving_time',
            'map',
            'name',
            'photos' 'start_date',
            'start_date_local',
            'start_latlng',
        ]
    )

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod  # noqa: C901
    def to_entity(cls, activity, parent=None, detailed_athlete=None):
        properties_dict = activity.to_dict()
        properties_dict['id'] = activity.id

        # We do a couple different things with athletes when we have them.
        if detailed_athlete:
            properties_dict['athlete'] = _AthleteConverter.to_entity(
                detailed_athlete, parent=parent
            )
        elif activity.athlete:
            properties_dict['athlete'] = _AthleteConverter.to_entity(
                activity.athlete, parent=parent
            )

        if activity.distance is not None:
            properties_dict['distance'] = activity.distance.num
        if activity.moving_time is not None:
            properties_dict['moving_time'] = activity.moving_time.seconds
        if activity.elapsed_time is not None:
            properties_dict['elapsed_time'] = activity.elapsed_time.seconds
        if activity.total_elevation_gain is not None:
            properties_dict['total_elevation_gain'] = activity.total_elevation_gain.num
        if activity.timezone is not None:
            properties_dict['timezone'] = str(activity.timezone)

        if activity.start_date is not None:
            properties_dict['start_date'] = activity.start_date.astimezone(
                pytz.UTC
            ).replace(tzinfo=None)

        if activity.start_date_local is not None:
            properties_dict['start_date_local'] = activity.start_date_local.replace(
                tzinfo=None
            )

        if activity.start_latlng is not None:
            properties_dict['start_latlng'] = GeoPoint(
                latitude=activity.start_latlng.lat, longitude=activity.start_latlng.lon
            )

        if activity.end_latlng is not None:
            properties_dict['end_latlng'] = GeoPoint(
                latitude=activity.end_latlng.lat, longitude=activity.end_latlng.lon
            )

        if activity.map is not None:
            properties_dict['map'] = _PolylineMapConverter.to_entity(activity.map)

        if activity.photos is not None:
            properties_dict['photos'] = _PhotosSummaryConverter.to_entity(
                activity.photos
            )

        if activity.average_speed is not None:
            properties_dict['average_speed'] = activity.average_speed.num

        if activity.max_speed is not None:
            properties_dict['max_speed'] = activity.max_speed.num

        # Some values we have to build, like if we get an activity from a club
        # request. It only populates a few fields:
        # ('name', 'Test Activity')
        # ('distance', 90764.4)
        # ('moving_time', '4:32:13')
        # ('elapsed_time', '5:57:06')
        # ('total_elevation_gain', 1988.4)
        # ('type', 'Ride')

        hash_string = hash_name(
            "{0:.0f}".format(
                activity.moving_time.seconds if activity.moving_time else 0
            ),
            "{0:.0f}".format(
                activity.elapsed_time.seconds if activity.elapsed_time else 0
            ),
            "{0:.0f}".format(activity.distance.num if activity.distance else 0),
            "{0:.0f}".format(
                activity.total_elevation_gain.num
                if activity.total_elevation_gain
                else 0
            ),
        )
        properties_dict['activity_hash'] = hash_string

        name = activity.id if activity.id else hash_string
        entity = Entity(
            ds_util.client.key('Activity', name, parent=parent),
            exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
        )
        entity.update(properties_dict)
        # entity.update(**dict(
        #    (k, v) for k, v
        #    in properties_dict.items() if k in [__STORED_FIELDS]))
        return entity


class _AthleteConverter(object):
    __ALL_FIELDS = SortedSet(
        [
            'admin',
            'agreed_to_terms',
            'approve_followers',
            'athlete_type',
            'badge_type_id',
            'bikes',
            'city',
            'clubs',
            'country',
            'created_at',
            'dateofbirth',
            'date_preference',
            'description',
            'email',
            'email_facebook_twitter_friend_joins',
            'email_kom_lost',
            'email_language',
            'email_send_follower_notices',
            'facebook_sharing_enabled',
            'firstname',
            'follower',
            'follower_count',
            'follower_request_count',
            'friend',
            'friend_count',
            'ftp',
            'global_privacy',
            'id',
            'instagram_username',
            'lastname',
            'max_heartrate',
            'measurement_preference',
            'membership',
            'mutual_friend_count',
            'offer_in_app_payment',
            'owner',
            'plan',
            'premium',
            'premium_expiration_date',
            'profile',
            'profile_medium',
            'profile_original',
            'receive_comment_emails',
            'receive_follower_feed_emails',
            'receive_kudos_emails',
            'receive_newsletter',
            'sample_race_distance',
            'sample_race_time',
            'sex',
            'shoes',
            'state',
            'subscription_permissions',
            'super_user',
            'updated_at',
            'username',
            'weight',
        ]
    )
    __INCLUDE_IN_INDEXES = SortedSet(
        [
            # Fields that /are/ included in indexes.
            'id',
            'clubs',
        ]
    )
    __STORED_FIELDS = SortedSet(['city', 'firstname', 'lastname' 'profileMedium'])

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, athlete, parent=None):
        properties_dict = athlete.to_dict()
        properties_dict['id'] = athlete.id

        # Some values are optional but need to be transformed.
        if athlete.weight is not None:
            properties_dict['weight'] = athlete.weight.num

        if athlete.created_at is not None:
            properties_dict['created_at'] = athlete.created_at.astimezone(
                pytz.UTC
            ).replace(tzinfo=None)

        if athlete.updated_at is not None:
            properties_dict['updated_at'] = athlete.updated_at.astimezone(
                pytz.UTC
            ).replace(tzinfo=None)

        # Some values are entities in and of themselves.
        if athlete.clubs is not None:
            properties_dict['clubs'] = [
                _ClubConverter.to_entity(club) for club in athlete.clubs
            ]

        if athlete.id is None:
            entity = Entity(
                ds_util.client.key('Athlete'),
                exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
            )
        else:
            entity = Entity(
                ds_util.client.key('Athlete', athlete.id, parent=parent),
                exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
            )
        entity.update(properties_dict)
        # entity.update(**dict(
        #    (k, v) for k, v
        #    in properties_dict.items() if k in [__STORED_FIELDS]))
        return entity


class _ClubConverter(object):
    __ALL_FIELDS = SortedSet(
        [
            'admin',
            'city',
            'club_type',
            'country',
            'cover_photo',
            'cover_photo_small',
            'description',
            'featured',
            'id',
            'member_count',
            'members',
            'membership',
            'name',
            'owner',
            'private',
            'profile',
            'profile_medium',
            'sport_type',
            'state',
            'url',
            'verified',
        ]
    )
    __INCLUDE_IN_INDEXES = SortedSet(
        [
            # Fields that /are/ included in indexes.
            'id',
            'admin',
        ]
    )
    __STORED_FIELDS = SortedSet([])

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, club, parent=None):
        properties_dict = club.to_dict()
        properties_dict['id'] = club.id

        entity = Entity(
            ds_util.client.key('Club', int(club.id), parent=parent),
            exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
        )
        entity.update(properties_dict)
        # entity.update(**dict(
        #    (k, v) for k, v
        #    in properties_dict.items() if k in [__STORED_FIELDS]))
        return entity


class _PhotosSummaryConverter(object):
    """DetailedActivity.photos"""

    __ALL_FIELDS = SortedSet(['count', 'primary'])
    __INCLUDE_IN_INDEXES = SortedSet([])
    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, photos_summary, parent=None):
        properties_dict = photos_summary.to_dict()

        if photos_summary.primary is not None:
            properties_dict['primary'] = _PhotosPrimaryConverter.to_entity(
                photos_summary.primary, parent=parent
            )

        entity = Entity(
            ds_util.client.key(
                'PhotosSummary',
                exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
            )
        )
        entity.update(properties_dict)
        return entity


class _PhotosPrimaryConverter(object):
    """DetailedActivity.photos.primary"""

    __ALL_FIELDS = SortedSet(['id', 'source', 'unique_id', 'urls'])
    __INCLUDE_IN_INDEXES = SortedSet(['id'])
    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, photos_primary, parent=None):
        properties_dict = photos_primary.to_dict()
        properties_dict['id'] = photos_primary.id

        entity = Entity(
            ds_util.client.key(
                'PhotosPrimary',
                exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
            )
        )
        entity.update(properties_dict)
        return entity


class _PolylineMapConverter(object):
    __ALL_FIELDS = SortedSet(['id', 'polyline', 'summary_polyline'])
    __INCLUDE_IN_INDEXES = SortedSet(['id'])
    __STORED_FIELDS = SortedSet(['polyline', 'summary_polyline'])

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, activity_map, parent=None):
        entity = Entity(
            ds_util.client.key('PolylineMap', parent=parent),
            exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
        )
        entity['id'] = activity_map.id
        entity['polyline'] = activity_map.polyline
        entity['summary_polyline'] = activity_map.summary_polyline
        return entity


class _RouteConverter(object):
    __ALL_FIELDS = SortedSet(['id'])
    __INCLUDE_IN_INDEXES = SortedSet(['id'])
    __STORED_FIELDS = SortedSet([])

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, route, parent=None):
        properties_dict = route.to_dict()
        properties_dict['id'] = route.id
        properties_dict['timestamp'] = datetime.datetime.fromtimestamp(
            route.timestamp
        ).replace(tzinfo=None)

        if route.athlete is not None:
            properties_dict['athlete'] = _AthleteConverter.to_entity(
                route.athlete, parent=parent
            )
        if route.map is not None:
            properties_dict['map'] = _PolylineMapConverter.to_entity(route.map)

        entity = Entity(
            ds_util.client.key(
                'Route',
                route.id,
                parent=parent,
                exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
            )
        )
        entity.update(properties_dict)
        return entity


class _SegmentConverter(object):
    __ALL_FIELDS = SortedSet(['id'])
    __INCLUDE_IN_INDEXES = SortedSet(['id'])
    __STORED_FIELDS = SortedSet([])

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, segment, elevations=None, parent=None):
        properties_dict = segment.to_dict()
        properties_dict['id'] = segment.id

        if segment.distance is not None:
            properties_dict['distance'] = segment.distance.num
        if segment.elevation_high is not None:
            properties_dict['elevation_high'] = segment.elevation_high.num
        if segment.elevation_low is not None:
            properties_dict['elevation_low'] = segment.elevation_low.num
        if segment.total_elevation_gain is not None:
            properties_dict['total_elevation_gain'] = segment.total_elevation_gain.num

        if segment.start_latlng is not None:
            properties_dict['start_latlng'] = GeoPoint(
                latitude=segment.start_latlng.lat, longitude=segment.start_latlng.lon
            )

        if segment.end_latlng is not None:
            properties_dict['end_latlng'] = GeoPoint(
                latitude=segment.end_latlng.lat, longitude=segment.end_latlng.lon
            )

        if segment.created_at is not None:
            properties_dict['created_at'] = segment.created_at.astimezone(
                pytz.UTC
            ).replace(tzinfo=None)

        if segment.updated_at is not None:
            properties_dict['updated_at'] = segment.updated_at.astimezone(
                pytz.UTC
            ).replace(tzinfo=None)

        if segment.map is not None:
            properties_dict['map'] = _PolylineMapConverter.to_entity(segment.map)

        if segment.starred_date is not None:
            properties_dict['starred_date'] = segment.starred_date.astimezone(
                pytz.UTC
            ).replace(tzinfo=None)

        if elevations:
            properties_dict['elevations'] = elevations

        entity = Entity(
            ds_util.client.key(
                'Segment',
                segment.id,
                parent=parent,
                exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
            )
        )
        entity.update(properties_dict)
        return entity


class _SegmentEffortConverter(object):
    __ALL_FIELDS = SortedSet(
        [
            'id',
            'elapsed_time',
            'start_date',
            'start_date_local',
            'distance',
            # 'is_kom',
            'name',
            'activity',
            'athlete',
            'moving_time',
            'start_index',
            'end_index',
            'average_cadence',
            'average_watts',
            'device_watts',
            'average_heartrate',
            'max_heartrate',
            'segment',
            'kom_rank',
            'pr_rank',
            'hidden',
        ]
    )
    __INCLUDE_IN_INDEXES = SortedSet(['id', 'segment_id', 'kom_rank'])
    __STORED_FIELDS = SortedSet(__ALL_FIELDS)
    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod  # noqa: C901
    def to_entity(cls, segment_effort, parent=None):
        properties_dict = segment_effort.to_dict()
        properties_dict['id'] = segment_effort.id
        properties_dict['segment_id'] = segment_effort.segment.id

        entity = Entity(
            ds_util.client.key('SegmentEffort', int(segment_effort.id), parent=parent),
            exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
        )
        if segment_effort.id is not None:
            properties_dict['id'] = segment_effort.id

        if segment_effort.elapsed_time is not None:
            properties_dict['elapsed_time'] = segment_effort.elapsed_time.seconds

        if segment_effort.start_date is not None:
            properties_dict['start_date'] = segment_effort.start_date.astimezone(
                pytz.UTC
            ).replace(tzinfo=None)

        if segment_effort.start_date_local is not None:
            properties_dict[
                'start_date_local'
            ] = segment_effort.start_date_local.replace(tzinfo=None)

        if segment_effort.distance is not None:
            properties_dict['distance'] = segment_effort.distance.num

        # if segment_effort.is_kom is not None:
        #     properties_dict['is_kom'] = segment_effort.is_kom

        if segment_effort.name is not None:
            properties_dict['name'] = segment_effort.name

        if segment_effort.activity is not None:
            properties_dict['activity'] = _ActivityConverter.to_entity(
                segment_effort.activity
            )

        if segment_effort.athlete is not None:
            properties_dict['athlete'] = _AthleteConverter.to_entity(
                segment_effort.athlete
            )

        if segment_effort.moving_time is not None:
            properties_dict['moving_time'] = segment_effort.moving_time.seconds

        if segment_effort.start_index is not None:
            properties_dict['start_index'] = segment_effort.start_index

        if segment_effort.end_index is not None:
            properties_dict['end_index'] = segment_effort.end_index

        if segment_effort.average_cadence is not None:
            properties_dict['average_cadence'] = segment_effort.average_cadence

        if segment_effort.average_watts is not None:
            properties_dict['average_watts'] = segment_effort.average_watts

        if segment_effort.device_watts is not None:
            properties_dict['device_watts'] = segment_effort.device_watts

        if segment_effort.average_heartrate is not None:
            properties_dict['average_heartrate'] = segment_effort.average_heartrate

        if segment_effort.max_heartrate is not None:
            properties_dict['max_heartrate'] = segment_effort.max_heartrate

        if segment_effort.segment is not None:
            properties_dict['segment'] = _SegmentConverter.to_entity(
                segment_effort.segment
            )

        if segment_effort.kom_rank is not None:
            properties_dict['kom_rank'] = segment_effort.kom_rank

        if segment_effort.pr_rank is not None:
            properties_dict['pr_rank'] = segment_effort.pr_rank

        if segment_effort.hidden is not None:
            properties_dict['hidden'] = segment_effort.hidden

        entity.update(properties_dict)
        return entity


class StravaConverters(object):
    Activity = _ActivityConverter
    Athlete = _AthleteConverter
    Club = _ClubConverter
    PolylineMap = _PolylineMapConverter
    Route = _RouteConverter
    Segment = _SegmentConverter
    SegmentEffort = _SegmentEffortConverter

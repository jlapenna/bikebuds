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

import hashlib
import logging
import pytz

from google.cloud.datastore.entity import Entity
from google.cloud.datastore.helpers import GeoPoint
from sortedcontainers import SortedSet

from shared import ds_util


class _ActivityConverter(object):
    __ALL_FIELDS = SortedSet([
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
            ])
    __INCLUDE_IN_INDEXES = SortedSet([
            'id',
            'start_date',
            ])
    __STORED_FIELDS = SortedSet([
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
            'start_date',
            'start_date_local',
            'start_latlng',
            ])

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)


    @classmethod
    def to_entity(cls, activity, parent=None, detailed_athlete=None):
        properties_dict = activity.to_dict()
        properties_dict['id'] = activity.id

        # We do a couple different things with athletes when we have them.
        if detailed_athlete:
            properties_dict['athlete'] = _AthleteConverter.to_entity(
                    detailed_athlete, parent=parent)
        elif activity.athlete:
            properties_dict['athlete'] = _AthleteConverter.to_entity(
                    activity.athlete, parent=parent)

        # Some values are always returned and always transformed.
        properties_dict.update(dict(
                distance=activity.distance.num,
                moving_time=activity.moving_time.seconds,
                elapsed_time=activity.elapsed_time.seconds,
                total_elevation_gain=activity.total_elevation_gain.num,
                timezone=str(activity.timezone),
                ))

        # Some values are optional but need to be transformed.
        if activity.start_date is not None:
            properties_dict['start_date'] = activity.start_date.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        if activity.start_date_local is not None:
            properties_dict['start_date_local'] = (
                    activity.start_date_local.replace(tzinfo=None))

        if activity.start_latlng is not None:
            properties_dict['start_latlng'] = GeoPoint(
                    latitude=activity.start_latlng.lat,
                    longitude=activity.start_latlng.lon)

        if activity.end_latlng is not None:
            properties_dict['end_latlng'] = GeoPoint(
                    latitude=activity.end_latlng.lat,
                    longitude=activity.end_latlng.lon)

        if activity.map is not None:
            properties_dict['map'] = dict(
                    polyline=activity.map.polyline,
                    summary_polyline=activity.map.summary_polyline,
            )

        if activity.average_speed is not None:
            properties_dict['average_speed'] = activity.average_speed.num

        if activity.max_speed is not None:
            properties_dict['max_speed'] = activity.max_speed.num

        # Some values we have to build.
        hash_string = '-'.join((
                activity.name,
                "{0:.0f}".format(activity.moving_time.seconds),
                "{0:.0f}".format(activity.elapsed_time.seconds),
                "{0:.0f}".format(activity.distance.num)
                ))
        properties_dict['activity_hash'] = hashlib.md5(hash_string.encode()).hexdigest()

        entity = Entity(
                ds_util.client.key('Activity', activity.id, parent=parent),
                exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES)
        entity.update(**properties_dict)
        #entity.update(**dict(
        #    (k, v) for k, v in properties_dict.items() if k in [STORED_FIELDS]))
        return entity


class _AthleteConverter(object):
    __ALL_FIELDS = SortedSet([
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
            ])
    __INCLUDE_IN_INDEXES = SortedSet([
            # Fields that /are/ included in indexes.
            'id',
            # 'clubs.id' ??
            ])
    __STORED_FIELDS = SortedSet([
            'city',
            'firstname',
            'lastname'
            'profileMedium',
            ])

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, athlete, parent=None, sub_ref=False):
        properties_dict = athlete.to_dict()
        properties_dict['id'] = athlete.id

        # Some values are always returned and always transformed.
        # ... not in Athlete.

        # Some values are optional but need to be transformed.
        if athlete.weight is not None:
            properties_dict['weight'] = athlete.weight.num

        if athlete.created_at is not None:
            properties_dict['created_at'] = athlete.created_at.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        if athlete.updated_at is not None:
            properties_dict['updated_at'] = athlete.updated_at.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        # Some values are entities in and of themselves.
        if athlete.clubs is not None:
            properties_dict['clubs'] = [_ClubConverter.to_entity(club) for club in athlete.clubs]

        if athlete.id is None:
            entity = Entity(ds_util.client.key('Athlete'),
                    exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES)
        else:
            entity = Entity(
                    ds_util.client.key('Athlete', athlete.id, parent=parent),
                    exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES)
        entity.update(**properties_dict)
        #entity.update(**dict(
        #    (k, v) for k, v in properties_dict.items() if k in [STORED_FIELDS]))
        return entity


class _ClubConverter(object):
    __ALL_FIELDS = SortedSet([
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
            ])
    __INCLUDE_IN_INDEXES = SortedSet([
            # Fields that /are/ included in indexes.
            'id',
            ])
    __STORED_FIELDS = SortedSet([
            ])

    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, club, parent=None, sub_ref=False):
        properties_dict = club.to_dict()
        properties_dict['id'] = club.id

        entity = Entity(
                ds_util.client.key('Club', club.id, parent=parent),
                exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES)
        entity.update(**properties_dict)
        #entity.update(**dict(
        #    (k, v) for k, v in properties_dict.items() if k in [STORED_FIELDS]))
        return entity


class StravaConverters(object):
    Activity = _ActivityConverter
    Athlete = _AthleteConverter
    Club = _ClubConverter

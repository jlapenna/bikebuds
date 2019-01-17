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
import dateutil.parser
import hashlib
import logging
import pytz
import sys

from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

from endpoints import message_types
from endpoints import messages

from measurement import measures

from shared.datastore import message_util
from shared.datastore.athlete_ref import AthleteRef, AthleteRefMessage


class GeoPtMessage(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)


class PolylineMapMessage(messages.Message):
    id = messages.StringField(1)
    polyline = messages.StringField(2)
    summary_polyline = messages.StringField(3)


class ActivityMessage(messages.Message):
    id = messages.IntegerField(1)
    athlete = messages.MessageField(AthleteRefMessage, 2)

    name = messages.StringField(3)
    distance = messages.FloatField(4)
    moving_time = messages.IntegerField(5)
    elapsed_time = messages.IntegerField(6)
    total_elevation_gain = messages.FloatField(7)
    elev_high = messages.FloatField(8)
    elev_low = messages.FloatField(9)
    activity_type = messages.StringField(10)
    start_date = message_types.DateTimeField(11)
    start_date_local = message_types.DateTimeField(12)
    timezone = messages.StringField(13)
    start_latlng = messages.MessageField(GeoPtMessage, 14)
    end_latlng = messages.MessageField(GeoPtMessage, 15)
    achievement_count = messages.IntegerField(16)
    kudos_count = messages.IntegerField(17)
    comment_count = messages.IntegerField(18)
    athlete_count = messages.IntegerField(19)
    photo_count = messages.IntegerField(20)
    total_photo_count = messages.IntegerField(21)
    map = messages.MessageField(PolylineMapMessage, 22)
    trainer = messages.BooleanField(23)
    commute = messages.BooleanField(24)
    manual = messages.BooleanField(25)
    private = messages.BooleanField(26)
    flagged = messages.BooleanField(27)
    workout_type = messages.StringField(28)
    average_speed = messages.FloatField(29)
    max_speed = messages.FloatField(30)
    has_kudoed = messages.BooleanField(31)
    gear_id = messages.StringField(32)
    kilojoules = messages.FloatField(33)
    average_watts = messages.FloatField(34)
    device_watts = messages.BooleanField(35)
    max_watts = messages.IntegerField(36)
    weighted_average_watts = messages.IntegerField(37)

    # DetailedActivity
    calories = messages.FloatField(38)
    description = messages.StringField(39)
    embed_token = messages.StringField(40)

    # Hacks
    activity_hash = messages.StringField(41)


class Activity(ndb.Model):
    # id = string
    activity = msgprop.MessageProperty(ActivityMessage,
            indexed_fields=['id', 'athlete.id'])
    start_date = ndb.DateTimeProperty(indexed=True)

    @classmethod
    def entity_from_strava(cls, parent_key, activity, detailed_athlete=None):
        activity_message = Activity.message_from_strava(activity,
                detailed_athlete=detailed_athlete)

        start_date = None
        if activity.start_date is not None:
            start_date = activity.start_date.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        return cls(id=activity.id, parent=parent_key,
                activity=activity_message,
                start_date=start_date)

    @classmethod
    def message_from_strava(cls, activity, detailed_athlete=None):
        athlete = None
        if detailed_athlete:
            athlete = AthleteRef.from_strava(detailed_athlete)
        elif activity.athlete:
            athlete = AthleteRef.from_strava(activity.athlete)

        start_date = None
        if activity.start_date is not None:
            start_date = activity.start_date.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        start_date_local = None
        if activity.start_date_local is not None:
            start_date_local = activity.start_date.replace(tzinfo=None)

        start_latlng = None
        if activity.start_latlng is not None:
            start_latlng = GeoPtMessage(
                    latitude=activity.start_latlng.lat,
                    longitude=activity.start_latlng.lon)

        end_latlng = None
        if activity.end_latlng is not None:
            end_latlng = GeoPtMessage(
                    latitude=activity.end_latlng.lat,
                    longitude=activity.end_latlng.lon)

        map_entity = None
        if activity.map is not None:
            map_entity = PolylineMapMessage(
                    id=activity.map.id,
                    polyline=activity.map.polyline,
                    summary_polyline=activity.map.summary_polyline)

        average_speed = None
        if activity.average_speed is not None:
            average_speed = activity.average_speed.num

        max_speed = None
        if activity.max_speed is not None:
            max_speed = activity.max_speed.num

        hash_string = '-'.join((
                activity.name.encode('ascii', 'ignore'),
                "{0:.0f}".format(activity.moving_time.seconds),
                "{0:.0f}".format(activity.elapsed_time.seconds),
                "{0:.0f}".format(activity.distance.num)
                ))
        activity_hash = hashlib.md5(hash_string.encode()).hexdigest()
        return ActivityMessage(
                id=activity.id,
                athlete=athlete,
                name=activity.name,
                distance=activity.distance.num,
                moving_time=activity.moving_time.seconds,
                elapsed_time=activity.elapsed_time.seconds,
                total_elevation_gain=activity.total_elevation_gain.num,
                elev_high=activity.elev_high,
                elev_low=activity.elev_low,
                activity_type=activity.type,
                start_date=start_date,
                start_date_local=start_date_local,
                timezone=str(activity.timezone),
                start_latlng=start_latlng,
                end_latlng=end_latlng,
                achievement_count=activity.achievement_count,
                kudos_count=activity.kudos_count,
                comment_count=activity.comment_count,
                athlete_count=activity.athlete_count,
                photo_count=activity.photo_count,
                total_photo_count=activity.total_photo_count,
                map = map_entity,
                trainer=activity.trainer,
                commute=activity.commute,
                manual=activity.manual,
                private=activity.private,
                flagged=activity.flagged,
                workout_type=activity.workout_type,
                average_speed=average_speed,
                max_speed=max_speed,
                has_kudoed=activity.has_kudoed,
                gear_id=activity.gear_id,
                kilojoules=activity.kilojoules,
                average_watts=activity.average_watts,
                device_watts=activity.device_watts,
                max_watts=activity.max_watts,
                weighted_average_watts=activity.weighted_average_watts,

                # DetailedActivity
                calories=activity.calories,
                description=activity.description,
                embed_token=activity.embed_token,

                # Hacks
                activity_hash=activity_hash
                )

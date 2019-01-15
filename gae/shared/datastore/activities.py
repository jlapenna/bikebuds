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

from endpoints import message_types
from endpoints import messages

from measurement import measures

from shared.datastore import message_util

class PolylineMap(ndb.Model):
    polyline = ndb.StringProperty(indexed=False)
    summary_polyline = ndb.StringProperty(indexed=False)

    @classmethod
    def to_message(cls, entity, *args, **kwargs):
        return message_util.to_message(
                PolylineMapMessage, entity,
                cls._to_message, *args, **kwargs)

    @classmethod
    def _to_message(cls, key, value, *args, **kwargs):
        return value


class Activity(ndb.Model):
    # id = string
    name = ndb.StringProperty(indexed=False)
    distance = ndb.FloatProperty(indexed=False)
    moving_time = ndb.IntegerProperty(indexed=False)
    elapsed_time = ndb.IntegerProperty(indexed=False)
    total_elevation_gain = ndb.FloatProperty(indexed=False)
    elev_high = ndb.FloatProperty(indexed=False)
    elev_low = ndb.FloatProperty(indexed=False)
    activity_type = ndb.StringProperty(indexed=False)
    start_date = ndb.DateTimeProperty(indexed=True)
    start_date_local = ndb.DateTimeProperty(indexed=False)
    timezone = ndb.StringProperty(indexed=False)
    start_latlng = ndb.GeoPtProperty(indexed=False)
    end_latlng = ndb.GeoPtProperty(indexed=False)
    achievement_count = ndb.IntegerProperty(indexed=False)
    kudos_count = ndb.IntegerProperty(indexed=False)
    comment_count = ndb.IntegerProperty(indexed=False)
    athlete_count = ndb.IntegerProperty(indexed=False)
    photo_count = ndb.IntegerProperty(indexed=False)
    total_photo_count = ndb.IntegerProperty(indexed=False)
    map = ndb.LocalStructuredProperty(PolylineMap, indexed=False)
    trainer = ndb.BooleanProperty(indexed=False)
    commute = ndb.BooleanProperty(indexed=False)
    manual = ndb.BooleanProperty(indexed=False)
    private = ndb.BooleanProperty(indexed=False)
    flagged = ndb.BooleanProperty(indexed=False)
    workout_type = ndb.StringProperty(indexed=False)
    average_speed = ndb.FloatProperty(indexed=False) # meters / second
    max_speed = ndb.FloatProperty(indexed=False)
    has_kudoed = ndb.BooleanProperty(indexed=False)
    gear_id = ndb.StringProperty(indexed=False)
    kilojoules = ndb.FloatProperty(indexed=False)
    average_watts = ndb.FloatProperty(indexed=False)
    device_watts = ndb.BooleanProperty(indexed=False)
    max_watts = ndb.IntegerProperty(indexed=False)
    weighted_average_watts = ndb.IntegerProperty(indexed=False)

    # DetailedActivity
    calories = ndb.FloatProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    embed_token = ndb.StringProperty(indexed=False)

    # Hacks
    activity_hash = ndb.StringProperty(indexed=True)

    strava_id = ndb.ComputedProperty(lambda self: self.key.id())

    @classmethod
    def from_strava(cls, parent_key, activity):
        start_date = None
        if activity.start_date is not None:
            start_date = activity.start_date.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        start_date_local = None
        if activity.start_date_local is not None:
            start_date_local = activity.start_date.replace(tzinfo=None)

        start_latlng = None
        if activity.start_latlng is not None:
            start_latlng = ndb.GeoPt(
                    activity.start_latlng.lat, activity.start_latlng.lon)

        end_latlng = None
        if activity.end_latlng is not None:
            end_latlng = ndb.GeoPt(
                    activity.end_latlng.lat, activity.end_latlng.lon)

        map_entity = None
        if activity.map is not None:
            map_entity = PolylineMap(id=activity.map.id,
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
        return Activity(
                id=activity.id,
                parent=parent_key,
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

    @classmethod
    def to_message(cls, entity, *args, **kwargs):
        return message_util.to_message(
                ActivityMessage, entity,
                cls._to_message, *args, **kwargs)
    
    @classmethod
    def _to_message(cls, key, value, *args, **kwargs):
        if key == 'strava_id':
            return None
        if key == 'start_latlng':
            return GeoPtMessage(
                    latitude=value.lat,
                    longitude=value.lon)
        if key == 'end_latlng':
            return GeoPtMessage(
                    latitude=value.lat,
                    longitude=value.lon)
        if key == 'map':
            return PolylineMap.to_message(value)
        return value


class GeoPtMessage(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)


class PolylineMapMessage(messages.Message):
    polyline = messages.StringField(2)
    summary_polyline = messages.StringField(3)


class ActivityMessage(messages.Message):
    id = messages.IntegerField(1)

    name = messages.StringField(2)
    distance = messages.FloatField(3)
    moving_time = messages.IntegerField(4)
    elapsed_time = messages.IntegerField(5)
    total_elevation_gain = messages.FloatField(6)
    elev_high = messages.FloatField(7)
    elev_low = messages.FloatField(8)
    activity_type = messages.StringField(9)
    start_date = message_types.DateTimeField(10)
    start_date_local = message_types.DateTimeField(11)
    timezone = messages.StringField(12)
    start_latlng = messages.MessageField(GeoPtMessage, 13)
    end_latlng = messages.MessageField(GeoPtMessage, 14)
    achievement_count = messages.IntegerField(15)
    kudos_count = messages.IntegerField(16)
    comment_count = messages.IntegerField(17)
    athlete_count = messages.IntegerField(18)
    photo_count = messages.IntegerField(19)
    total_photo_count = messages.IntegerField(20)
    map = messages.MessageField(PolylineMapMessage, 21)
    trainer = messages.BooleanField(22)
    commute = messages.BooleanField(23)
    manual = messages.BooleanField(24)
    private = messages.BooleanField(25)
    flagged = messages.BooleanField(26)
    workout_type = messages.StringField(27)
    average_speed = messages.FloatField(28)
    max_speed = messages.FloatField(29)
    has_kudoed = messages.BooleanField(30)
    gear_id = messages.StringField(31)
    kilojoules = messages.FloatField(32)
    average_watts = messages.FloatField(33)
    device_watts = messages.BooleanField(34)
    max_watts = messages.IntegerField(35)
    weighted_average_watts = messages.IntegerField(36)

    # DetailedActivity
    calories = messages.FloatField(37)
    description = messages.StringField(38)
    embed_token = messages.StringField(39)

    # Hacks
    activity_hash = messages.StringField(40)

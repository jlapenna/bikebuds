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

from shared import ds_util


class _ActivityConverter(object):

    @classmethod
    def to_entity(cls, activity, parent=None, detailed_athlete=None):
        activity_dict = activity.to_dict()
        activity_dict['id'] = activity.id

        # We do a couple differnt things with athletes when we have them.
        if detailed_athlete:
            activity_dict['athlete'] = _AthleteConverter.to_entity(
                    detailed_athlete, parent=parent)
        elif activity.athlete:
            activity_dict['athlete'] = _AthleteConverter.to_entity(
                    activity.athlete, parent=parent)

        # Some values are always returned and always transformed.
        activity_dict.update(dict(
                distance=activity.distance.num,
                moving_time=activity.moving_time.seconds,
                elapsed_time=activity.elapsed_time.seconds,
                total_elevation_gain=activity.total_elevation_gain.num,
                timezone=str(activity.timezone),
                ))

        # Some values are optional but need to be transformed.
        if activity.start_date is not None:
            activity_dict['start_date'] = activity.start_date.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        if activity.start_date_local is not None:
            activity_dict['start_date_local'] = activity.start_date_local.replace(tzinfo=None)

        if activity.start_latlng is not None:
            activity_dict['start_latlng'] = GeoPoint(
                    latitude=activity.start_latlng.lat,
                    longitude=activity.start_latlng.lon)

        if activity.end_latlng is not None:
            activity_dict['end_latlng'] = GeoPoint(
                    latitude=activity.end_latlng.lat,
                    longitude=activity.end_latlng.lon)

        if activity.map is not None:
            activity_dict['map'] = dict(
                    polyline=activity.map.polyline,
                    summary_polyline=activity.map.summary_polyline,
            )

        if activity.average_speed is not None:
            activity_dict['average_speed'] = activity.average_speed.num

        if activity.max_speed is not None:
            activity_dict['max_speed'] = activity.max_speed.num

        # Some values we have to build.
        hash_string = '-'.join((
                activity.name,
                "{0:.0f}".format(activity.moving_time.seconds),
                "{0:.0f}".format(activity.elapsed_time.seconds),
                "{0:.0f}".format(activity.distance.num)
                ))
        activity_dict['activity_hash'] = hashlib.md5(hash_string.encode()).hexdigest()

        entity = Entity(ds_util.client.key('Activity', activity.id, parent=parent))
        entity.update(**activity_dict)
        return entity


class _AthleteConverter(object):

    @classmethod
    def to_entity(cls, athlete, parent=None):
        athlete_dict = athlete.to_dict()
        athlete_dict['id'] = athlete.id

        # Some values are always returned and always transformed.
        # ... not in Athlete.

        # Some values are optional but need to be transformed.
        if athlete.weight is not None:
            athlete_dict['weight'] = athlete.weight.num

        if athlete.created_at is not None:
            athlete_dict['created_at'] = athlete.created_at.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        if athlete.updated_at is not None:
            athlete_dict['updated_at'] = athlete.updated_at.astimezone(
                    pytz.UTC).replace(tzinfo=None)

        # Some values are entities in and of themselves.
        if athlete.clubs is not None:
            athlete_dict['clubs'] = [_ClubConverter.to_entity(club) for club in athlete.clubs]

        if athlete.id is None:
            entity = Entity(ds_util.client.key('Athlete'))
        else:
            entity = Entity(ds_util.client.key('Athlete', athlete.id, parent=parent))
        entity.update(**athlete_dict)
        return entity


class _ClubConverter(object):
    @classmethod
    def to_entity(cls, club, parent=None):
        club_dict = club.to_dict()
        club_dict['id'] = club.id

        entity = Entity(ds_util.client.key('Club', club.id, parent=parent))
        entity.update(**club_dict)
        return entity

class StravaConverters(object):
    Activity = _ActivityConverter
    Athlete = _AthleteConverter
    Club = _ClubConverter

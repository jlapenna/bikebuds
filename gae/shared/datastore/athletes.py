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

import dateutil.parser
import logging
import pytz
import sys

from google.appengine.ext import ndb

from endpoints import message_types
from endpoints import messages

from measurement import measures

from shared.datastore.clubs import Club, ClubMessage


class Athlete(ndb.Model):
    # id = string
    resource_state = ndb.IntegerProperty(indexed=False)
    firstname = ndb.StringProperty(indexed=False)
    lastname = ndb.StringProperty(indexed=False)
    profile_medium = ndb.StringProperty(indexed=False)
    profile = ndb.StringProperty(indexed=False)
    city = ndb.StringProperty(indexed=False)
    state = ndb.StringProperty(indexed=False)
    country = ndb.StringProperty(indexed=False)
    sex = ndb.StringProperty(indexed=False)
    friend = ndb.StringProperty(indexed=False)
    follower = ndb.StringProperty(indexed=False)
    premium = ndb.BooleanProperty(indexed=False)
    #summit = ndb.BooleanProperty(indexed=False)  # Not returned by stravalib
    created_at = ndb.DateTimeProperty(indexed=False)
    updated_at = ndb.DateTimeProperty(indexed=False)
    follower_count = ndb.IntegerProperty(indexed=False)
    friend_count = ndb.IntegerProperty(indexed=False)
    mutual_friend_count = ndb.IntegerProperty(indexed=False)
    measurement_preference = ndb.StringProperty(indexed=False)
    ftp = ndb.StringProperty(indexed=False)
    weight = ndb.FloatProperty(indexed=False)
    clubs = ndb.StructuredProperty(Club, indexed=True, repeated=True)
    # bikes = [SummaryGear, ...]
    # shoes = [SummaryGear, ...]

    @classmethod
    def from_strava(cls, service_key, athlete):
        clubs = []
        if athlete.clubs is not None:
            clubs = [Club.from_strava(service_key, club)
                     for club in athlete.clubs]
        if athlete.weight is None:
            weight = None
        else:
            weight = athlete.weight.num
        return Athlete(
                id=athlete.id,
                parent=service_key,
                resource_state=athlete.resource_state,
                firstname=athlete.firstname,
                lastname=athlete.lastname,
                profile_medium=athlete.profile_medium,
                profile=athlete.profile,
                city=athlete.city,
                state=athlete.state,
                country=athlete.country,
                sex=athlete.sex,
                friend=athlete.friend,
                follower=athlete.follower,
                premium=athlete.premium,
                #summit=athlete.summit,  # Not returned by stravalib
                created_at=athlete.created_at.astimezone(
                        pytz.UTC).replace(tzinfo=None),
                updated_at=athlete.updated_at.astimezone(
                        pytz.UTC).replace(tzinfo=None),
                follower_count=athlete.follower_count,
                friend_count=athlete.friend_count,
                mutual_friend_count=athlete.mutual_friend_count,
                measurement_preference=athlete.measurement_preference,
                ftp=athlete.ftp,
                weight=weight,
                clubs=clubs)

    @classmethod
    def to_message(cls, athlete, to_imperial=True):
        attributes = {}
        for key in cls._properties:
            value = getattr(athlete, key, None)
            if value is None:
                continue
            try:
                attributes[key] = cls._convert(key, value, to_imperial)
            except Exception, e:
                msg = 'Unable to convert: %s (%s) -> %s' % (
                        key, value, sys.exc_info()[1])
                raise Exception, Exception(msg), sys.exc_info()[2]
        return AthleteMessage(id=athlete.key.id(), **attributes)
    
    @classmethod
    def _convert(cls, key, value, to_imperial):
        if key == 'clubs':
            clubs = []
            return [Club.to_message(club, to_imperial=to_imperial)
                    for club in value]
        return value

    @classmethod
    def get_private(cls, service_key):
        athletes = Athlete.query(ancestor=service_key).fetch(1)
        if athletes is None:
            return None
        else:
            return athletes[0]


class AthleteMessage(messages.Message):
    id = messages.IntegerField(1)
    resource_state = messages.IntegerField(2)
    firstname = messages.StringField(3)
    lastname = messages.StringField(4)
    profile_medium = messages.StringField(5)
    profile = messages.StringField(6)
    city = messages.StringField(7)
    state = messages.StringField(8)
    country = messages.StringField(9)
    sex = messages.StringField(10)
    friend = messages.StringField(11)
    follower = messages.StringField(12)
    premium = messages.BooleanField(13)
    #summit = messages.BooleanField(14)  # Not returned by stravalib
    created_at = message_types.DateTimeField(15)
    updated_at = message_types.DateTimeField(16)
    follower_count = messages.IntegerField(17)
    friend_count = messages.IntegerField(18)
    mutual_friend_count = messages.IntegerField(19)
    measurement_preference = messages.StringField(20)
    ftp = messages.StringField(21)
    weight = messages.FloatField(22)
    clubs = messages.MessageField(ClubMessage, 23, repeated=True)
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

import pytz

from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

from endpoints import message_types
from endpoints import messages

from shared.datastore.club_ref import ClubRef, ClubRefMessage
from shared.datastore import message_util


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
    clubs = messages.MessageField(ClubRefMessage, 23, repeated=True)


class Athlete(ndb.Model):
    # id = string
    athlete = msgprop.MessageProperty(AthleteMessage, indexed_fields=['id', 'clubs.id'])

    @classmethod
    def entity_from_strava(cls, service_key, athlete):
        athlete_message = cls.message_from_strava(athlete)
        return cls(id=athlete.id, parent=service_key,
                athlete=athlete_message)

    @classmethod
    def message_from_strava(cls, athlete):
        weight = None
        if athlete.weight is not None:
            weight = athlete.weight.num

        clubs = []
        if athlete.clubs is not None:
            clubs = [ClubRef.from_strava(club) for club in athlete.clubs]

        return AthleteMessage(
                id=athlete.id,
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
    def get_private(cls, service_key):
        athletes = Athlete.query(ancestor=service_key).fetch(1)
        if athletes is None or len(athletes) == 0:
            return None
        else:
            return athletes[0]

    @classmethod
    def get_by_id(cls, strava_id, keys_only=False):
        athletes = Athlete.query(
                Athlete.athlete.id == strava_id).fetch(1, keys_only=True)
        if athletes is None or len(athletes) == 0:
            return None
        else:
            return athletes[0]

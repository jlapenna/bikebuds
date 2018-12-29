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

from shared.datastore import message_util


class AthleteRef(ndb.Model):
    key = ndb.KeyProperty(indexed=True)
    firstname = ndb.StringProperty(indexed=False)
    lastname = ndb.StringProperty(indexed=False)
    profile_medium = ndb.StringProperty(indexed=False)
    profile = ndb.StringProperty(indexed=False)

    @classmethod
    def from_strava(cls, athlete):
        return cls(
                key=ndb.Key(cls, athlete.id),
                firstname=athlete.firstname,
                lastname=athlete.lastname,
                profile_medium=athlete.profile_medium,
                profile=athlete.profile)

    @classmethod
    def from_entity(cls, athlete):
        return cls(
                key=ndb.Key(cls, athlete.key.id()),
                firstname=athlete.firstname,
                lastname=athlete.lastname,
                profile_medium=athlete.profile_medium,
                profile=athlete.profile)

    @classmethod
    def to_message(cls, entity, *args, **kwargs):
        return message_util.to_message(
                AthleteRefMessage, entity,
                cls._to_message, *args, **kwargs)
    
    @classmethod
    def _to_message(cls, key, value, *args, **kwargs):
        if key == 'key':
            return None
        return value


class Club(ndb.Model):
    # id = string
    resource_state = ndb.IntegerProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    profile_medium = ndb.StringProperty(indexed=False)
    cover_photo = ndb.StringProperty(indexed=False)
    cover_photo_small = ndb.StringProperty(indexed=False)
    sport_type = ndb.StringProperty(indexed=False)
    city = ndb.StringProperty(indexed=False)
    state = ndb.StringProperty(indexed=False)
    country = ndb.StringProperty(indexed=False)
    private = ndb.BooleanProperty(indexed=False)
    member_count = ndb.IntegerProperty(indexed=False)
    featured = ndb.BooleanProperty(indexed=False)
    verified = ndb.BooleanProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)

    # Non-strava info.
    members = ndb.StructuredProperty(AthleteRef, repeated=True)

    @classmethod
    def from_strava(cls, club):
        return cls(
                id=club.id,
                resource_state=club.resource_state,
                name=club.name,
                profile_medium=club.profile_medium,
                cover_photo=club.cover_photo,
                cover_photo_small=club.cover_photo_small,
                sport_type=club.sport_type,
                city=club.city,
                state=club.state,
                country=club.country,
                private=club.private,
                member_count=club.member_count,
                featured=club.featured,
                verified=club.verified,
                url=club.url)

    @classmethod
    def to_message(cls, entity, *args, **kwargs):
        return message_util.to_message(
                ClubMessage, entity,
                cls._to_message, *args, **kwargs)
    
    @classmethod
    def _to_message(cls, key, value, *args, **kwargs):
        if key == 'members':
            return [AthleteRef.to_message(member) for member in value]
        return value


class AthleteRefMessage(messages.Message):
    id = messages.IntegerField(1)
    firstname = messages.StringField(2)
    lastname = messages.StringField(3)
    profile_medium = messages.StringField(4)
    profile = messages.StringField(5)


class ClubMessage(messages.Message):
    id = messages.IntegerField(1)
    resource_state = messages.IntegerField(2)
    name = messages.StringField(3)
    profile_medium = messages.StringField(4)
    cover_photo = messages.StringField(5)
    cover_photo_small = messages.StringField(6)
    sport_type = messages.StringField(7)
    city = messages.StringField(8)
    state = messages.StringField(9)
    country = messages.StringField(10)
    private = messages.BooleanField(11)
    member_count = messages.IntegerField(12)
    featured = messages.BooleanField(13)
    verified = messages.BooleanField(14)
    url = messages.StringField(15)

    # Non-strava info.
    members = messages.MessageField(AthleteRefMessage, 16, repeated=True)

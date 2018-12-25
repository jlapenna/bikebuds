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


class Club(ndb.Model):
    # id = string
    club_id = ndb.IntegerProperty(indexed=True)
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


    @classmethod
    def from_strava(cls, service_key, club):
        return Club(
                id=club.id,
                club_id=club.id,
                parent=service_key,
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
    def to_message(cls, club, to_imperial=True):
        attributes = {}
        for key in cls._properties:
            value = getattr(club, key, None)
            if value is None:
                continue
            try:
                attributes[key] = cls._convert(key, value, to_imperial)
            except Exception, e:
                msg = 'Unable to convert: %s (%s) -> %s' % (
                        key, value, sys.exc_info()[1])
                raise Exception, Exception(msg), sys.exc_info()[2]
        if club.key is None:
            club_id = club.club_id
        else:
            club_id = club.key.id()
        return ClubMessage(id=club_id, **attributes)
    
    @classmethod
    def _convert(cls, key, value, to_imperial):
        return value


class ClubMessage(messages.Message):
    id = messages.IntegerField(1)
    club_id = messages.IntegerField(2)
    resource_state = messages.IntegerField(3)
    name = messages.StringField(4)
    profile_medium = messages.StringField(5)
    cover_photo = messages.StringField(6)
    cover_photo_small = messages.StringField(7)
    sport_type = messages.StringField(8)
    city = messages.StringField(9)
    state = messages.StringField(10)
    country = messages.StringField(11)
    private = messages.BooleanField(12)
    member_count = messages.IntegerField(13)
    featured = messages.BooleanField(14)
    verified = messages.BooleanField(15)
    url = messages.StringField(16)

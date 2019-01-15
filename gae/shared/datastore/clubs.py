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

from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

from endpoints import messages

from shared.datastore import message_util
from shared.datastore.athlete_ref import AthleteRef, AthleteRefMessage


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

    members = messages.MessageField(AthleteRefMessage, 16, repeated=True)


class Club(ndb.Model):
    # id = string
    club = msgprop.MessageProperty(ClubMessage)

    @classmethod
    def entity_from_strava(cls, club):
        club_message = cls.message_from_strava(club)
        return cls(id=club.id, club=club_message)

    @classmethod
    def message_from_strava(cls, club):
        return ClubMessage(
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

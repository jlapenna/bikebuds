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

from endpoints import messages

from shared.datastore import message_util


class ClubRefMessage(messages.Message):
    id = messages.IntegerField(1)
    name = messages.StringField(2)
    profile_medium = messages.StringField(3)
    url = messages.StringField(4)
    admin = messages.BooleanField(5)
    owner = messages.BooleanField(6)


class ClubRef(object):

    @classmethod
    def from_strava(cls, club):
        return ClubRefMessage(
                id=club.id,
                name=club.name,
                profile_medium=club.profile_medium,
                url=club.url,
                admin=club.admin,
                owner=club.owner)

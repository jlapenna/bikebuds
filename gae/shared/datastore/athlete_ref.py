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


class AthleteRefMessage(messages.Message):
    id = messages.IntegerField(1)
    firstname = messages.StringField(2)
    lastname = messages.StringField(3)
    profile_medium = messages.StringField(4)
    profile = messages.StringField(5)


class AthleteRef(object):

    @classmethod
    def from_strava(cls, athlete):
        return AthleteRefMessage(
                id=athlete.id,
                firstname=athlete.firstname,
                lastname=athlete.lastname,
                profile_medium=athlete.profile_medium,
                profile=athlete.profile)

    @classmethod
    def from_athlete_message(cls, athlete):
        return AthleteRefMessage(
                id=athlete.id,
                firstname=athlete.firstname,
                lastname=athlete.lastname,
                profile_medium=athlete.profile_medium,
                profile=athlete.profile)

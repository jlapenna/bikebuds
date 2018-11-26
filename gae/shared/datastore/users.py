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

# Module supporting storing user info.

from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

from endpoints import messages


class PreferencesMessage(messages.Message):
    class Unit(messages.Enum):
        UNKNOWN = 0
        IMPERIAL = 1
        METRIC = 2
    units = messages.EnumField(Unit, 1,
            default=Unit.IMPERIAL)


def default_preferences():
    return PreferencesMessage(units=PreferencesMessage.Unit.IMPERIAL)


class User(ndb.Model):
    """Holds user info."""
    name = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    preferences = msgprop.MessageProperty(PreferencesMessage,
            default=default_preferences())

    @classmethod
    def get(cls, claims):
        return User.get_or_insert(claims['sub'])

    @classmethod
    def get_key(cls, claims):
        return ndb.Key(User, claims['sub'])

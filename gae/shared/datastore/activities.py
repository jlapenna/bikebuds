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

from google.appengine.ext import ndb

from endpoints import message_types
from endpoints import messages


class Activity(ndb.Model):
    name = ndb.StringProperty()
    start_date = ndb.DateTimeProperty()
    moving_time = ndb.IntegerProperty(indexed=False)
    elapsed_time = ndb.IntegerProperty(indexed=False)

    @classmethod
    def from_strava(cls, service_key, activity):
        start_date = activity.start_date.astimezone(pytz.UTC).replace(
                tzinfo=None)
        return Activity(
                id=activity.id,
                parent=service_key,
                name=activity.name,
                start_date=start_date,
                moving_time=activity.moving_time.seconds,
                elapsed_time=activity.elapsed_time.seconds)

    @classmethod
    def to_message(cls, activity, to_imperial=True):
        attributes = {}
        for key in cls._properties:
            value = getattr(activity, key, None)
            if value is None:
                continue
            attributes[key] = cls._convert(key, value, to_imperial)
        return ActivityMessage(id=activity.key.id(), **attributes)
    
    @classmethod
    def _convert(cls, key, value, to_imperial):
        if to_imperial:
            return cls._convert_imperial(key, value)
        else:
            return cls._convert_metric(key, value)
    
    @classmethod
    def _convert_imperial(cls, key, value):
        if key == 'distance':
            return measures.Distance(meter=value).mi
        return value
    
    @classmethod
    def _convert_metric(cls, key, value):
        return value


class ActivityMessage(messages.Message):
    id = messages.IntegerField(1)

    name = messages.StringField(2)
    start_date = message_types.DateTimeField(3)
    moving_time = messages.IntegerField(4)
    elapsed_time = messages.IntegerField(5)

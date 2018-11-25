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

import datetime
import logging
import math
import time

from google.appengine.ext import ndb

from endpoints import message_types
from endpoints import messages

from measurement import measures

import nokia 

_KG_TO_POUNDS = 2.20462262185

class Measure(ndb.Model):
    """Holds a measure."""
    date = ndb.DateTimeProperty()

    weight = ndb.FloatProperty()  # 1
    height = ndb.FloatProperty(indexed=False)  # 4
    fat_free_mass = ndb.FloatProperty(indexed=False)  # 5
    fat_ratio = ndb.FloatProperty(indexed=False)  # 6
    fat_mass_weight = ndb.FloatProperty(indexed=False)  # 8
    diastolic_blood_pressure = ndb.FloatProperty(indexed=False)  # 9
    systolic_blood_pressure = ndb.FloatProperty(indexed=False)  # 10
    heart_pulse = ndb.FloatProperty(indexed=False)  # 11
    temperature = ndb.FloatProperty(indexed=False)  # 12
    spo2 = ndb.FloatProperty(indexed=False)  # 54
    body_temperature = ndb.FloatProperty(indexed=False)  # 71
    skin_temperature = ndb.FloatProperty(indexed=False)  # 72
    muscle_mass = ndb.FloatProperty(indexed=False)  # 76
    hydration = ndb.FloatProperty(indexed=False)  # 77
    bone_mass = ndb.FloatProperty(indexed=False)  # 88
    pulse_wave_velocity = ndb.FloatProperty(indexed=False)  # 91

    @classmethod
    def from_withings(cls, service_key, measure):
        attributes = dict()
        for key, type_int in nokia.NokiaMeasureGroup.MEASURE_TYPES:
            value = measure.get_measure(type_int)
            if value is not None:
                attributes[key] = value
        measure = Measure(
                id=measure.date.timestamp,
                parent=service_key,
                date=measure.date.datetime.replace(tzinfo=None),
                **attributes)
        return measure

    @classmethod
    def from_fitbit_time_series(cls, service_key, measure):
        date = datetime.datetime.strptime(
                measure['dateTime'], '%Y-%m-%d')
        measure = Measure(
                id=date.strftime('%s'),
                parent=service_key,
                date=date,
                weight=float(measure['value']),
                )
        return measure

    @classmethod
    def from_fitbit_log(cls, service_key, measure):
        date = datetime.datetime.strptime(
                measure['date'] + ' ' + measure['time'], '%Y-%m-%d %H:%M:%S')
        measure = Measure(id=measure['logId'],
                parent=service_key,
                date=date,
                weight=measure['weight'],
                fat_ratio=measure['fat'],
                )
        return measure

    @classmethod
    def latest_query(cls, service_key, measure_type):
        return Measure.query(measure_type != None, ancestor=service_key).order(
                measure_type, -Measure.date)

    @classmethod
    def fetch_lastupdate(cls, service_key):
        return Measure.query(ancestor=service_key).order(-Measure.date).fetch(1)


    @classmethod
    def to_message(cls, measure, to_imperial=True):
        attributes = dict()
        for key, _ in nokia.NokiaMeasureGroup.MEASURE_TYPES:
            value = getattr(measure, key, None)
            if value is None:
                continue
            attributes[key] = cls._convert(key, value, to_imperial)
        measure = MeasureMessage(date=measure.date, **attributes)
        return measure
    
    @classmethod
    def _convert(cls, key, value, to_imperial):
        if to_imperial:
            return cls._convert_imperial(key, value)
        else:
            return cls._convert_metric(key, value)
    
    @classmethod
    def _convert_imperial(cls, key, value):
        if key == 'weight':
            return measures.Weight(kg=value).lb
        if key == 'height':
            height = measures.Distance(meter=value)
            return '%s\'%s"' % (height.ft, math.modf(height.ft)[0] * 12)
        return value
    
    @classmethod
    def _convert_metric(cls, key, value):
        if key == 'height':
            return str(value)
        return value


class MeasureMessage(messages.Message):
    id = messages.StringField(1)
    date = message_types.DateTimeField(2)

    weight = messages.FloatField(3)  # 1
    height = messages.StringField(4)  # 4
    fat_free_mass = messages.FloatField(5)  # 5
    fat_ratio = messages.FloatField(6)  # 6
    fat_mass_weight = messages.FloatField(7)  # 8
    diastolic_blood_pressure = messages.FloatField(8)  # 9
    systolic_blood_pressure = messages.FloatField(9)  # 10
    heart_pulse = messages.FloatField(10)  # 11
    temperature = messages.FloatField(11)  # 12
    spo2 = messages.FloatField(12)  # 54
    body_temperature = messages.FloatField(13)  # 71
    skin_temperature = messages.FloatField(14)  # 72
    muscle_mass = messages.FloatField(15)  # 76
    hydration = messages.FloatField(16)  # 77
    bone_mass = messages.FloatField(17)  # 88
    pulse_wave_velocity = messages.FloatField(18)  # 91

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
import sys
import time

from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

from endpoints import message_types
from endpoints import messages

import nokia 


class MeasureMessage(messages.Message):
    id = messages.StringField(1)

    date = message_types.DateTimeField(2)
    weight = messages.FloatField(3)  # 1
    height = messages.FloatField(4)  # 4
    fat_free_mass = messages.FloatField(5)  # 5
    fat_ratio = messages.FloatField(6)  # 6
    fat_mass_weight = messages.FloatField(7)  # 8
    diastolic_blood_pressure = messages.IntegerField(8)  # 9
    systolic_blood_pressure = messages.IntegerField(9)  # 10
    heart_pulse = messages.IntegerField(10)  # 11
    temperature = messages.FloatField(11)  # 12
    spo2 = messages.FloatField(12)  # 54
    body_temperature = messages.FloatField(13)  # 71
    skin_temperature = messages.FloatField(14)  # 72
    muscle_mass = messages.FloatField(15)  # 76
    hydration = messages.FloatField(16)  # 77
    bone_mass = messages.FloatField(17)  # 88
    pulse_wave_velocity = messages.FloatField(18)  # 91


class _Util(object):

    @classmethod
    def message_from_withings(cls, measure):
        attributes = dict()
        for key, type_int in nokia.NokiaMeasureGroup.MEASURE_TYPES:
            value = measure.get_measure(type_int)
            if value is not None:
                attributes[key] = value
        return MeasureMessage(
                id=str(measure.date.timestamp),
                date=measure.date.datetime.replace(tzinfo=None),
                **attributes)

    @classmethod
    def message_from_fitbit_time_series(cls, measure):
        date = datetime.datetime.strptime(
                measure['dateTime'], '%Y-%m-%d')
        return MeasureMessage(
                id=date.strftime('%s'),
                date=date,
                weight=float(measure['value']),
                )

    @classmethod
    def message_from_fitbit_log(cls, measure):
        date = datetime.datetime.strptime(
                measure['date'] + ' ' + measure['time'], '%Y-%m-%d %H:%M:%S')
        return MeasureMessage(
                id=measure['logId'],
                date=date,
                weight=measure['weight'],
                fat_ratio=measure['fat'],
                )


class SeriesMessage(messages.Message):
    measures = messages.MessageField(MeasureMessage, 2, repeated=True)


class Series(ndb.Model):
    """Holds a series of measures."""
    series = msgprop.MessageProperty(SeriesMessage, indexed=['measures.measure_type', 'measures.date'])

    @classmethod
    def entity_from_withings(cls, service_key, measures, id="default"):
        measures = [_Util.message_from_withings(m) for m in measures]
        series = SeriesMessage(measures=measures)
        return Series(id=id, parent=service_key, series=series)

    @classmethod
    def entity_from_fitbit_time_series(cls, service_key, measures, id="default"):
        measures = [_Util.message_from_fitbit_time_series(m) for m in measures]
        series = SeriesMessage(measures=measures)
        return Series(id=id, parent=service_key, series=series)

    @classmethod
    def entity_from_fitbit_log(cls, service_key, measures, id="default"):
        measures = [_Util.message_from_fitbit_log(m) for m in measures]
        series = SeriesMessage(measures=measures)
        return Series(id=id, parent=service_key, series=series)

    @classmethod
    def get_default(cls, parent):
        return ndb.Key(cls, "default", parent=parent).get()

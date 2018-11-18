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

import nokia 


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
    def to_measure(cls, service_key, measure):
        attributes = dict()
        for key, type_int in nokia.NokiaMeasureGroup.MEASURE_TYPES:
            value = measure.get_measure(type_int)
            if value is not None:
                attributes[key] = value
        measure = Measure(id=measure.date.timestamp,
                parent=service_key,
                date=measure.date.datetime.replace(tzinfo=None),
                **attributes)
        return measure

    @classmethod
    def latest_query(cls, service_key, measure_type):
        return Measure.query(measure_type != None, ancestor=service_key).order(
                measure_type, -Measure.date)

    @classmethod
    def fetch_lastupdate(cls, service_key):
        return Measure.query(ancestor=service_key).order(-Measure.date).fetch(1)

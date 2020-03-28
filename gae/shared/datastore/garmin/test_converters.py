# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import unittest

from google.cloud.datastore.entity import Entity

from shared import ds_util
from shared.datastore.garmin.converters import GarminConverters


class GarminConvertersTest(unittest.TestCase):
    def test_measures(self):
        measure_item = BODY_COMP['dateWeightList'][0]
        entity = GarminConverters.Measure.to_entity(measure_item)
        expected_entity = Entity(ds_util.client.key('Measure'))
        expected_entity.update(
            {
                'date': datetime.datetime(2020, 3, 22, 1, 49),
                'fat_ratio': None,
                'weight': 59.4206,
            }
        )
        self.assertEqual(entity.items(), expected_entity.items())


STATS = {
    'userProfileId': 84356213,
    'displayName': 'c6c6405d-e641-421b-8cf9-278493e18f2e',
    'totalKilocalories': None,
    'activeKilocalories': None,
    'bmrKilocalories': None,
    'wellnessKilocalories': None,
    'burnedKilocalories': None,
    'consumedKilocalories': None,
    'remainingKilocalories': None,
    'totalSteps': None,
    'netCalorieGoal': None,
    'totalDistanceMeters': None,
    'wellnessDistanceMeters': None,
    'wellnessActiveKilocalories': None,
    'netRemainingKilocalories': 0.0,
    'userDailySummaryId': None,
    'calendarDate': '2020-03-27',
    'rule': None,
    'uuid': None,
    'dailyStepGoal': None,
    'wellnessStartTimeGmt': None,
    'wellnessStartTimeLocal': None,
    'wellnessEndTimeGmt': None,
    'wellnessEndTimeLocal': None,
    'durationInMilliseconds': None,
    'wellnessDescription': None,
    'highlyActiveSeconds': None,
    'activeSeconds': None,
    'sedentarySeconds': None,
    'sleepingSeconds': None,
    'includesWellnessData': False,
    'includesActivityData': False,
    'includesCalorieConsumedData': False,
    'privacyProtected': False,
    'moderateIntensityMinutes': None,
    'vigorousIntensityMinutes': None,
    'floorsAscendedInMeters': None,
    'floorsDescendedInMeters': None,
    'floorsAscended': None,
    'floorsDescended': None,
    'intensityMinutesGoal': None,
    'userFloorsAscendedGoal': None,
    'minHeartRate': None,
    'maxHeartRate': None,
    'restingHeartRate': None,
    'lastSevenDaysAvgRestingHeartRate': None,
    'source': 'GARMIN',
    'averageStressLevel': None,
    'maxStressLevel': None,
    'stressDuration': None,
    'restStressDuration': None,
    'activityStressDuration': None,
    'uncategorizedStressDuration': None,
    'totalStressDuration': None,
    'lowStressDuration': None,
    'mediumStressDuration': None,
    'highStressDuration': None,
    'stressPercentage': None,
    'restStressPercentage': None,
    'activityStressPercentage': None,
    'uncategorizedStressPercentage': None,
    'lowStressPercentage': None,
    'mediumStressPercentage': None,
    'highStressPercentage': None,
    'stressQualifier': None,
    'measurableAwakeDuration': None,
    'measurableAsleepDuration': None,
    'lastSyncTimestampGMT': None,
    'minAvgHeartRate': None,
    'maxAvgHeartRate': None,
    'bodyBatteryChargedValue': None,
    'bodyBatteryDrainedValue': None,
    'bodyBatteryHighestValue': None,
    'bodyBatteryLowestValue': None,
    'bodyBatteryMostRecentValue': None,
    'abnormalHeartRateAlertsCount': None,
    'averageSpo2': None,
    'lowestSpo2': None,
    'latestSpo2': None,
    'latestSpo2ReadingTimeGmt': None,
    'latestSpo2ReadingTimeLocal': None,
    'averageMonitoringEnvironmentAltitude': None,
}

BODY_COMP = {
    'startDate': '2020-03-21',
    'endDate': '2020-03-28',
    'dateWeightList': [
        {
            'samplePk': 1584928169694,
            'date': 1584816540000,
            'calendarDate': '2020-03-21',
            'weight': 59420.600470000005,
            'bmi': None,
            'bodyFat': None,
            'bodyWater': None,
            'boneMass': None,
            'muscleMass': None,
            'physiqueRating': None,
            'visceralFat': None,
            'metabolicAge': None,
            'sourceType': 'MANUAL',
            'timestampGMT': 1584841740000,
            'weightDelta': None,
        },
        {
            'samplePk': 1584928117642,
            'date': 1584902880000,
            'calendarDate': '2020-03-22',
            'weight': 53523.89966,
            'bmi': None,
            'bodyFat': None,
            'bodyWater': None,
            'boneMass': None,
            'muscleMass': None,
            'physiqueRating': None,
            'visceralFat': None,
            'metabolicAge': None,
            'sourceType': 'MANUAL',
            'timestampGMT': 1584928080000,
            'weightDelta': -5896.70081,
        },
        {
            'samplePk': 1585326189714,
            'date': 1584955320000,
            'calendarDate': '2020-03-23',
            'weight': 53977.49203,
            'bmi': None,
            'bodyFat': None,
            'bodyWater': None,
            'boneMass': None,
            'muscleMass': None,
            'physiqueRating': None,
            'visceralFat': None,
            'metabolicAge': None,
            'sourceType': 'MANUAL',
            'timestampGMT': 1584980520000,
            'weightDelta': 453.59237,
        },
        {
            'samplePk': 1585326197626,
            'date': 1585041780000,
            'calendarDate': '2020-03-24',
            'weight': 54431.0844,
            'bmi': None,
            'bodyFat': None,
            'bodyWater': None,
            'boneMass': None,
            'muscleMass': None,
            'physiqueRating': None,
            'visceralFat': None,
            'metabolicAge': None,
            'sourceType': 'MANUAL',
            'timestampGMT': 1585066980000,
            'weightDelta': 453.59237,
        },
    ],
    'totalAverage': {
        'from': 1584748800000,
        'until': 1585439999999,
        'weight': 55338.26914,
        'bmi': None,
        'bodyFat': None,
        'bodyWater': None,
        'boneMass': None,
        'muscleMass': None,
        'physiqueRating': None,
        'visceralFat': None,
        'metabolicAge': None,
        'weightCount': 4,
        'bmiCount': 0,
        'bodyFatCount': 0,
        'bodyWaterCount': 0,
        'boneMassCount': 0,
        'muscleMassCount': 0,
        'physiqueRatingCount': 0,
        'visceralFatCount': 0,
        'metabolicAgeCount': 0,
    },
}

PREFS = {
    'powerFormat': {
        'minFraction': 0,
        'formatKey': 'watt',
        'maxFraction': 0,
        'formatId': 30,
        'displayFormat': None,
        'groupingUsed': True,
    },
    'measurementSystem': 'statute_us',
    'hydrationContainers': [],
    'hydrationMeasurementUnit': 'cup',
    'preferredLocale': 'en',
    'timeFormat': {
        'displayFormat': 'h:mm a',
        'groupingUsed': False,
        'minFraction': 0,
        'formatKey': 'time_twelve_hr',
        'maxFraction': 0,
        'formatId': 32,
    },
    'dateFormat': {
        'formatId': 23,
        'displayFormat': 'EEE, MMM d, yyyy',
        'groupingUsed': False,
        'minFraction': 0,
        'formatKey': 'mmddyyyy',
        'maxFraction': 0,
    },
    'numberFormat': 'decimal_period',
    'firstDayOfWeek': {
        'dayName': 'sunday',
        'dayId': 2,
        'isPossibleFirstDay': True,
        'sortOrder': 2,
    },
    'timeZone': 'gmt',
    'heartRateFormat': {
        'displayFormat': None,
        'groupingUsed': False,
        'minFraction': 0,
        'formatKey': 'bpm',
        'maxFraction': 0,
        'formatId': 21,
    },
    'displayName': 'c6c6405d-e641-421b-8cf9-278493e18f2e',
}

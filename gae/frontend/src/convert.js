/**
 * Copyright 2019 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import momentTimezone from 'moment-timezone';
import moment from 'moment';
import convert from 'convert-units';

export function localMoment(dateMoment) {
  return momentTimezone.tz(dateMoment, momentTimezone.tz.guess());
}

export function readableDuration(seconds, profile) {
  return moment.duration(seconds, 'seconds').format('hh:mm:ss');
}

export function readableDistance(meters, profile) {
  if (meters === undefined) {
    return undefined;
  }
  if (getUnitPref(profile) === 'IMPERIAL') {
    return (
      convert(meters)
        .from('m')
        .to('mi')
        .toFixed(2) + 'mi'
    );
  } else {
    return (
      convert(meters)
        .from('m')
        .to('km')
        .toFixed(2) + 'km'
    );
  }
}

export function readableElevation(meters, profile) {
  if (meters === undefined) {
    return undefined;
  }
  if (getUnitPref(profile) === 'IMPERIAL') {
    return (
      convert(meters)
        .from('m')
        .to('ft')
        .toFixed(2) + 'ft'
    );
  } else {
    return (
      convert(meters)
        .from('m')
        .to('m')
        .toFixed(2) + 'm'
    );
  }
}

export function readableSpeed(meters_per_second, profile) {
  if (!meters_per_second) {
    return undefined;
  }
  var speed = convert(meters_per_second)
    .from('m/s')
    .to('km/h');
  if (getUnitPref(profile) === 'IMPERIAL') {
    return (
      convert(speed)
        .from('km')
        .to('mi')
        .toFixed(2) + 'mph'
    );
  } else {
    return speed.toFixed(2) + 'km/h';
  }
}

export function readableWeight(weight, profile) {
  if (weight === undefined) {
    return undefined;
  }
  if (weight === null) {
    return null;
  }
  if (getUnitPref(profile) === 'IMPERIAL') {
    return Number(
      convert(weight)
        .from('kg')
        .to('lb')
        .toFixed(1)
    );
  } else {
    return Number(weight.toFixed(1));
  }
}

function getUnitPref(profile) {
  if (profile === undefined) {
    return undefined;
  }
  if (profile.user === undefined) {
    return undefined;
  }
  return profile.user.properties.preferences.units;
}

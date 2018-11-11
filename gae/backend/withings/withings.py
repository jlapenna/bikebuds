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

import json
import logging
import os

from google.appengine.ext import ndb

import flask
from flask_cors import cross_origin

import nokia 

import auth_util
from shared.datastore import users
from shared.config import config
from shared.datastore import services


SERVICE_NAME = 'withings'

module = flask.Blueprint(SERVICE_NAME, __name__,
        template_folder='templates',
        static_folder='static')


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


@module.route('/withings/test', methods=['GET', 'POST'])
@auth_util.claims_required
def test(claims):
    user = users.User.get(claims)
    service_creds = services.ServiceCredentials.default(user.key, SERVICE_NAME)
    if service_creds is None:
        return get_auth_url_response()
    service_key = services.Service.get_key(user.key, SERVICE_NAME)

    # TODO: pass a refresh_cb function to store refreshed tokens
    client = nokia.NokiaApi(service_creds)
    measures = client.get_measures(lastupdate=lastupdate, category=1)

    logging.info(str(dir(Measure.weight)))
    query = Measure.latest_query(service_key, Measure.weight)
    logging.info(query)
    results = query.fetch(1)
    logging.info(results)
    return flask.make_response('OK', 200)


@module.route('/withings/sync', methods=['GET', 'POST'])
@auth_util.claims_required
def sync(claims):
    user = users.User.get(claims)
    service_creds = services.ServiceCredentials.default(user.key, SERVICE_NAME)
    if service_creds is None:
        return get_auth_url_response()
    service_key = services.Service.get_key(user.key, SERVICE_NAME)

    lastupdate = flask.request.args.get('lastupdate', None)
    if lastupdate is None:
        latest = Measure.fetch_lastupdate(service_key)
        if len(latest) == 1:
            lastupdate = latest[0].key.id()
        else:
            lastupdate = 0
    logging.info('lastupdate: ' + str(lastupdate))

    # TODO: pass a refresh_cb function to store refreshed tokens
    client = nokia.NokiaApi(service_creds)

    measures = client.get_measures(lastupdate=lastupdate, category=1)
    logging.info('lenthg: ' + str(len(measures)))

    @ndb.transactional
    def put_measures(measures, service_key):
        for measure in measures:
            Measure.to_measure(service_key, measure).put()
    put_measures(measures, service_key)
    return flask.make_response('OK', 200)


@module.route('/withings/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    user = users.User.get(claims)
    service = services.Service.get(user.key, SERVICE_NAME)

    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/withings/redirect', methods=['GET'])
@cross_origin(origins=['https://www.withings.com'])
@auth_util.claims_required
def redirect(claims):
    user = users.User.get(claims)
    service = services.Service.get(user.key, SERVICE_NAME)

    code = flask.request.args.get('code')
    dest = flask.request.args.get('dest', '')

    auth = nokia.NokiaAuth(config.withings_creds['client_id'],
            config.withings_creds['client_secret'],
            callback_uri=get_callback_uri(dest))
    creds = auth.get_credentials(code)

    creds_dict = dict(
            access_token=creds.access_token,
            token_expiry=creds.token_expiry,
            token_type=creds.token_type,
            refresh_token=creds.refresh_token,
            user_id=creds.user_id,
            client_id=creds.client_id,
            consumer_secret=creds.consumer_secret)
    service_creds = services.ServiceCredentials.update(user.key, SERVICE_NAME,
        creds_dict)

    dest = flask.request.args.get('dest', '')
    return flask.redirect(config.backend_url + dest)


def get_callback_uri(dest):
    return config.backend_url + '/withings/redirect?dest=' + dest


def get_auth_url_response(dest):
    auth = nokia.NokiaAuth(config.withings_creds['client_id'],
            config.withings_creds['client_secret'],
            callback_uri=get_callback_uri(dest))
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': auth.get_authorize_url()})
    else:
        return flask.redirect(auth.get_authorize_url())

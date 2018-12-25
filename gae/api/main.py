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

"""Bikebuds API."""

from shared import monkeypatch

import logging
import datetime

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import endpoints
from endpoints import message_types
from endpoints import messages
from endpoints import remote

import auth_util
from shared.datastore.measures import Measure, MeasureMessage, Series, SeriesMessage
from shared.datastore.activities import Activity, ActivityMessage
from shared.datastore.services import Service, ServiceMessage, ServiceCredentials
from shared.datastore.users import User, PreferencesMessage


class RequestHeader(messages.Message):
    pass


class ResponseHeader(messages.Message):
    pass


class Request(messages.Message):
    header = messages.MessageField(RequestHeader, 1)


class Response(messages.Message):
    """A proto Message that contains a simple string field."""
    header = messages.MessageField(ResponseHeader, 1)


class ActivitiesResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    activities = messages.MessageField(ActivityMessage, 2, repeated=True)


class MeasuresResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    measures = messages.MessageField(MeasureMessage, 2, repeated=True)


class SeriesResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    series = messages.MessageField(SeriesMessage, 2)


class PreferencesResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    preferences = messages.MessageField(PreferencesMessage, 2)


class UpdatePreferencesRequest(messages.Message):
    header = messages.MessageField(RequestHeader, 1)
    preferences = messages.MessageField(PreferencesMessage, 2)


class ProfileResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    created = message_types.DateTimeField(2)


class ServiceResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    service = messages.MessageField(ServiceMessage, 2)


class UpdateServiceRequest(messages.Message):
    header = messages.MessageField(RequestHeader, 1)
    service = messages.MessageField(ServiceMessage, 2)


@endpoints.api(
    name='bikebuds',
    version='v1',
    issuers={'firebase': endpoints.Issuer(
        'https://securetoken.google.com/bikebuds-app',
        'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'
        # Using this (per some documentation...) is wrong...
        #'https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com'
        )},
    audiences={'firebase': 'bikebuds-app'}
    )
class BikebudsApi(remote.Service):

    @endpoints.method(
        endpoints.ResourceContainer(Request),
        ActivitiesResponse,
        path='activities',
        http_method='POST',
        api_key_required=True)
    def get_activities(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = User.get(claims)
        to_imperial = user.preferences.units == PreferencesMessage.Unit.IMPERIAL

        response = ActivitiesResponse(activities=[])
        for activity in Activity.query().order(-Activity.start_date):
            response.activities.append(
                    Activity.to_message(activity, to_imperial=to_imperial))
        return response

    @endpoints.method(
        endpoints.ResourceContainer(Request),
        SeriesResponse,
        path='series',
        http_method='POST',
        api_key_required=True)
    def get_series(self, request):
        logging.info('Beginning auth')
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        logging.info('Beginning claims')
        claims = auth_util.verify_claims_from_header(self.request_state)
        logging.info('Finished claims')
        user = User.get(claims)
        logging.info('Finished user')

        to_imperial = (user.preferences.units ==
                PreferencesMessage.Unit.IMPERIAL)

        logging.info('Beginning series')
        result = Series.get_default(Service.get_key(user.key, 'withings'))
        if result is None:
            return SeriesResponse()
        logging.info('Finished series')
        return SeriesResponse(series=Series.to_message(result, to_imperial))

    @endpoints.method(
        Request,
        PreferencesResponse,
        path='preferences',
        http_method='POST',
        api_key_required=True)
    def get_preferences(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = User.get(claims)
        preferences = user.preferences or users.default_preferences()
        return PreferencesResponse(preferences=preferences)

    @endpoints.method(
        UpdatePreferencesRequest,
        PreferencesResponse,
        path='update_preferences',
        http_method='POST',
        api_key_required=True)
    def update_preferences(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = User.get(claims)
        user.preferences = request.preferences
        user.put()
        return PreferencesResponse(preferences=user.preferences)

    @endpoints.method(
        Request,
        ProfileResponse,
        path='profile',
        http_method='POST',
        api_key_required=True)
    def get_profile(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = User.get(claims)
        return ProfileResponse(created=user.created)

    @endpoints.method(
        endpoints.ResourceContainer(Request, id=messages.StringField(1)),
        ServiceResponse,
        path='service/{id}',
        http_method='POST',
        api_key_required=True)
    def get_service(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = User.get(claims)
        service = Service.get(user.key, request.id)
        service_creds = service.get_credentials()
        return ServiceResponse(service=Service.to_message(service))

    @endpoints.method(
        endpoints.ResourceContainer(UpdateServiceRequest,
            id=messages.StringField(1)),
        ServiceResponse,
        path='update_service/{id}',
        http_method='POST',
        api_key_required=True)
    def update_service(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = User.get(claims)
        service = Service.get(user.key, request.id)
        service_creds = service.get_credentials()
        if request.service.sync_enabled is not None:
            service.sync_enabled = request.service.sync_enabled
            service.put()
        return ServiceResponse(service=Service.to_message(service))

    @endpoints.method(
        endpoints.ResourceContainer(Request, id=messages.StringField(1)),
        ServiceResponse,
        path='service_sync/{id}',
        http_method='POST',
        api_key_required=True)
    def sync_service(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = User.get(claims)
        logging.info('Getting %s service info.', request.id)
        service = Service.get(user.key, request.id)

        @ndb.transactional
        def submit_sync():
            service.syncing=True
            service.sync_date=datetime.datetime.now()
            service.sync_successful=None
            service.put()
            taskqueue.add(
                    url='/tasks/service_sync/' + service.key.id(),
                    target='backend',
                    params={
                        'user': user.key.urlsafe(),
                        'service': service.key.urlsafe()},
                    transactional=True)
        submit_sync()
        return ServiceResponse(service=Service.to_message(service))

    @endpoints.method(
        endpoints.ResourceContainer(Request, id=messages.StringField(2)),
        ServiceResponse,
        path='service_disconnect/{id}',
        http_method='POST',
        api_key_required=True)
    def disconnect_service(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = User.get(claims)
        logging.info('Getting %s service info.', request.id)
        service = Service.get(user.key, request.id)
        service.clear_credentials()
        return ServiceResponse(service=Service.to_message(service))


api = endpoints.api_server([BikebudsApi])

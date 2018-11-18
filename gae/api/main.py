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

import logging
import datetime

import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import endpoints
from endpoints import message_types
from endpoints import messages
from endpoints import remote

import auth_util
from shared.datastore import services
from shared.datastore import users
from shared.services.withings import withings


class RequestHeader(messages.Message):
    pass


class ResponseHeader(messages.Message):
    pass


class Request(messages.Message):
    header = messages.MessageField(RequestHeader, 1)


class Response(messages.Message):
    """A proto Message that contains a simple string field."""
    header = messages.MessageField(ResponseHeader, 1)


class MeasuresResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    measure = messages.MessageField(withings.MeasureMessage, 2, repeated=True)


class ProfileResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    created = message_types.DateTimeField(2)


class ServiceResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    created = message_types.DateTimeField(2)
    modified = message_types.DateTimeField(3)
    connected = messages.BooleanField(4)
    syncing = messages.BooleanField(5)
    sync_date = message_types.DateTimeField(6)
    sync_successful = messages.BooleanField(7)


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
        ProfileResponse,
        path='profile',
        http_method='POST',
        api_key_required=True)
    def get_profile(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = users.User.get(claims)
        response = ProfileResponse(created=user.created)
        return response

    @endpoints.method(
        endpoints.ResourceContainer(Request, id=messages.StringField(2)),
        ServiceResponse,
        path='service/{id}',
        http_method='POST',
        api_key_required=True)
    def get_service(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = users.User.get(claims)
        logging.info('Getting %s service info.', request.id)
        service = services.Service.get(user.key, request.id)
        service_creds = services.ServiceCredentials.default(user.key, request.id)
        return ServiceResponse(created=service.created,
                modified=service.modified,
                syncing=service.syncing,
                sync_date=service.sync_date,
                sync_successful=service.sync_successful,
                connected=service_creds is not None)

    @endpoints.method(
        endpoints.ResourceContainer(Request, id=messages.StringField(2)),
        ServiceResponse,
        path='sync/{id}',
        http_method='POST',
        api_key_required=True)
    def sync_service(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = users.User.get(claims)
        logging.info('Getting %s service info.', request.id)
        service = services.Service.get(user.key, request.id)

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
        return ServiceResponse(created=service.created,
                modified=service.modified,
                connected=True)

    @endpoints.method(
        endpoints.ResourceContainer(Request),
        MeasuresResponse,
        path='measures',
        http_method='POST',
        api_key_required=True)
    def measures(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = users.User.get(claims)
        service = services.Service.get(user.key, 'withings')
        service_creds = services.ServiceCredentials.default(user.key, 'withings')
        measures = withings.Measure.query()
        proto_measures = []
        for measure in measures:
            proto_measures.append(withings.create_message(measure))

        return MeasuresResponse(measure=proto_measures)

    @endpoints.method(
        endpoints.ResourceContainer(Request, id=messages.StringField(2)),
        ServiceResponse,
        path='disconnect/{id}',
        http_method='POST',
        api_key_required=True)
    def disconnect_service(self, request):
        if not endpoints.get_current_user():
            raise endpoints.UnauthorizedException('Unable to identify user.')
        claims = auth_util.verify_claims_from_header(self.request_state)
        user = users.User.get(claims)
        logging.info('Getting %s service info.', request.id)
        service = services.Service.get(user.key, request.id)
        services.ServiceCredentials.get_key(service.key).delete()
        return ServiceResponse(created=service.created,
                modified=service.modified,
                connected=False)


api = endpoints.api_server([BikebudsApi])

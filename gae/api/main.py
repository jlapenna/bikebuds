"""Bikebuds API."""

import logging
logging.getLogger('endpoints').setLevel(logging.DEBUG)
logging.getLogger('endpoints_management').setLevel(logging.DEBUG)

import google.auth.transport.requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

import endpoints
from endpoints import message_types
from endpoints import messages
from endpoints import remote

import auth_util
from shared.datastore import services
from shared.datastore import users


class RequestHeader(messages.Message):
    pass


class ResponseHeader(messages.Message):
    pass


class Request(messages.Message):
    header = messages.MessageField(RequestHeader, 1)


class Response(messages.Message):
    """A proto Message that contains a simple string field."""
    header = messages.MessageField(ResponseHeader, 1)


class ProfileResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    created = message_types.DateTimeField(2)


class ServiceResponse(messages.Message):
    header = messages.MessageField(ResponseHeader, 1)
    created = message_types.DateTimeField(2)
    modified = message_types.DateTimeField(3)
    connected = messages.BooleanField(4)


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
        response = ServiceResponse(created=service.created,
                modified=service.modified,
                connected=service_creds is not None)
        return response

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
        response = ServiceResponse(created=service.created,
                modified=service.modified,
                connected=False)
        return response

    @endpoints.method(
        message_types.VoidMessage,
        Response,
        http_method='GET',
        api_key_required=True)
    def get_api_key(self, request):
        key, key_type = request.get_unrecognized_field_info('key')
        return Response(content=key)


api = endpoints.api_server([BikebudsApi])

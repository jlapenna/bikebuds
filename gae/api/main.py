"""Bikebuds API."""

import logging
logging.getLogger('endpoints').setLevel(logging.DEBUG)
logging.getLogger('endpoints_management').setLevel(logging.DEBUG)

import endpoints
from endpoints import message_types
from endpoints import messages
from endpoints import remote


class BikebudsRequest(messages.Message):
    content = messages.StringField(1)

class BikebudsResponse(messages.Message):
    """A proto Message that contains a simple string field."""
    content = messages.StringField(1)

BIKEBUDS_RESOURCE = endpoints.ResourceContainer(
    BikebudsRequest)


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
        BIKEBUDS_RESOURCE,
        BikebudsResponse,
        path='test',
        http_method='POST',
        name='test')
    def test(self, request):
        output_content = request.content
        return BikebudsResponse(content=output_content)

    @endpoints.method(
        message_types.VoidMessage,
        BikebudsResponse,
        path='getUser',
        http_method='GET',
        name='get_user',
        api_key_required=True)
    def get_user(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Unable to identify user.')
        return BikebudsResponse(content=str(user))

    @endpoints.method(
        message_types.VoidMessage,
        BikebudsResponse,
        path='getApiKey',
        http_method='GET',
        name='get_api_key',
        api_key_required=True)
    def get_api_key(self, request):
        key, key_type = request.get_unrecognized_field_info('key')
        return BikebudsResponse(content=key)


api = endpoints.api_server([BikebudsApi])

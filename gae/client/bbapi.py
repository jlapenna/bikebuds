#!/usr/bin/env python3

from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client as SwagClient

from shared.config import config

import startup

oauth_credentials = startup.run_flow()

# Autheticates against the Bikebuds API using google-based oauth identity.
# I can't figure out how to do this with firebase identity
swag_app = App._create_(config.api_url + '/bikebudsv1openapi.json')
swag_auth = Security(swag_app)
swag_auth.update_with('api_key', config.python_client_testing_api_key)

api_client = SwagClient(swag_auth)
api_client._Client__s.headers['Authorization'] = 'Bearer ' + oauth_credentials.id_token
# This is a hack for my server, auth_util.verify_claims by default tries to
# validate via firebase.
api_client._Client__s.headers['UseAltAuth'] = '1'

req, resp = swag_app.op['getProfile'](body=None)
req.produce('application/json')
api_client.request((req, resp))
print(resp.status)
print(resp.data)

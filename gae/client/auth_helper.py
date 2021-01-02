#!/usr/bin/env python3
#
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

import json
import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from shared.config import config

import bikebuds_api


def load_credentials():
    try:
        creds = json.load(open('.credentials.json', 'r'))
        flow_creds = Credentials(**creds)
    except FileNotFoundError:
        flow_creds = None
    if not (flow_creds and flow_creds.valid):
        print('Unable to load credentials!')
        return None

    flow_creds.refresh(Request())
    return flow_creds


def load_configuration(flow_creds):
    configuration = bikebuds_api.Configuration()
    configuration.host = config.api_url

    # Configure API key authorization: api_key
    configuration.api_key['key'] = config.gcp_server_creds['api_key']

    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # configuration.api_key_prefix['key'] = 'Bearer'

    # Configure OAuth2 access token for authorization: firebase
    configuration.access_token = flow_creds.id_token
    return configuration


def run_flow():
    oauth_flow = InstalledAppFlow.from_client_secrets_file(
        os.path.join(config.base_path, 'service_keys/server-oauth.json'),
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ],
    )
    return oauth_flow.run_local_server(host='localhost', port=0, open_browser=True)


def fetch_credentials():
    flow_creds = run_flow()
    if not flow_creds.valid:
        print('Unable to complete creds flow!')
    creds = {
        'client_id': flow_creds.client_id,
        'client_secret': flow_creds.client_secret,
        'id_token': flow_creds.id_token,
        'refresh_token': flow_creds.refresh_token,
        'scopes': flow_creds.scopes,
        'token': flow_creds.token,
        'token_uri': flow_creds.token_uri,
    }
    json.dump(creds, open('.credentials.json', 'w'))

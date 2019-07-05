#!/usr/bin/env python3

import collections

from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud.datastore import Client
from google.cloud.datastore.key import Key
from google.oauth2.service_account import Credentials

from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client as SwagClient
from pyswagger.utils import jp_compose

from shared.config import config
from shared import ds_util

# OAuth to Google - Gets a google ID token, access token & refresh token.
oauth_flow = InstalledAppFlow.from_client_secrets_file(
        os.path.join(config.base_path, 
        'service_keys/python-client-testing-oauth.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile']))

def run_flow():
    return flow.run_local_server(host='localhost', port=8095,
            open_browser=True)

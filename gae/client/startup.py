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

# Datastore Client
ds_credentials = Credentials.from_service_account_file(
        'lib/env/service_keys/python-client-testing.json')
ds_client = Client(project=config.project_id, credentials=ds_credentials)

# Common name for ds client in actual server. Convenience.
DsUtil = collections.namedtuple('DsUtil', 'client')
ds_util = DsUtil(client=ds_client)

# OAuth to Google - Gets a google ID token, access token & refresh token.
oauth_flow = InstalledAppFlow.from_client_secrets_file(
        'lib/env/service_keys/python-client-testing-oauth.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'])

def run_flow():
    return flow.run_local_server(host='localhost', port=8095,
            open_browser=True)

#!/usr/bin/env python3

import logging  # noqa: F401
import os

from google_auth_oauthlib import flow
from google.cloud.datastore import Client  # noqa: F401
from google.cloud.datastore.key import Key  # noqa: F401

from shared.config import config  # noqa: F401
from shared import ds_util  # noqa: F401
from shared import task_util  # noqa: F401

# OAuth to Google - Gets a google ID token, access token & refresh token.
oauth_flow = flow.InstalledAppFlow.from_client_secrets_file(
    os.path.join(config.base_path, 'service_keys/python-client-testing-oauth.json'),
    scopes=[
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
    ],
)


def run_flow():
    return flow.run_local_server(host='localhost', port=8095, open_browser=True)

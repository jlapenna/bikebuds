#!/usr/bin/env python3
#
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from shared.config import config


def main():
    creds_path = os.path.join(
        os.environ.get('BIKEBUDS_ENV'),
        'service_keys/gcp-server-oauth.json',
    )
    flow = InstalledAppFlow.from_client_secrets_file(
        creds_path,
        ['https://www.googleapis.com/auth/gmail.readonly'],
    )
    creds = flow.run_local_server(port=0, open_browser=False)
    service = build('gmail', 'v1', credentials=creds)

    # Configure gmail to send pushes
    request = {
        'labelIds': ['INBOX'],
        'topicName': 'projects/%s/topics/rides' % (config.project_id,),
    }
    watch = service.users().watch(userId='me', body=request).execute()
    print(watch)


if __name__ == '__main__':
    main()

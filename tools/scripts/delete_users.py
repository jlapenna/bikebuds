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

import argparse
import logging
import os

import firebase_admin
from firebase_admin import auth
from firebase_admin.credentials import Certificate

from google.cloud.datastore import Client


def main(is_uid, users):
    # client = Client(project=config.project_id)
    creds_path = os.path.join(
        os.environ.get('BIKEBUDS_ENV'),
        'service_keys/firebase-adminsdk.json',
    )
    client = Client.from_service_account_json(creds_path)
    for u in users:
        logging.info('Deleting: %s', u)
        if is_uid:
            uid = u
        else:
            logging.info('Looking up: %s', u)
            uid = auth.get_user_by_email(u).uid
        try:
            key = client.key('User', uid)
            if client.get(key) is not None:
                children_query = client.query(ancestor=key)
                children_query.keys_only()
                client.delete_multi(child.key for child in children_query.fetch())
            else:
                logging.warning('Could not cleanup datastore for: %s', u)
        except Exception:
            logging.warning('Could not delete datastore user: %s', u)

        try:
            auth.delete_user(uid)
        except auth.UserNotFoundError:
            logging.warning('Could not delete firebase user: %s', u)
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--uid', action='store_true')
    parser.add_argument('users', nargs='+')
    args = parser.parse_args()

    creds_path = os.path.join(
        os.environ.get('BIKEBUDS_ENV'),
        'service_keys/firebase-adminsdk.json',
    )
    creds = Certificate(creds_path)
    firebase_admin.initialize_app(creds)

    main(args.uid, args.users)

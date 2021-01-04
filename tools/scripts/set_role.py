#!/usr/bin/env python3
#
# Copyright 2019 Google LLC
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
import os

import firebase_admin
from firebase_admin import auth
from firebase_admin.credentials import Certificate


def main(email, role):
    try:
        user = auth.get_user_by_email(email)
    except auth.UserNotFoundError:
        user = auth.create_user(email=email, email_verified=True)
    auth.set_custom_user_claims(user.uid, {'role': role})
    print('Added %s role to %s' % (role, email))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('email')
    parser.add_argument('role')
    args = parser.parse_args()

    creds_path = os.path.join(
        os.environ.get('BIKEBUDS_ENV'),
        'service_keys/firebase-adminsdk.json',
    )
    creds = Certificate(creds_path)
    firebase_admin.initialize_app(creds)

    main(args.email, args.role)

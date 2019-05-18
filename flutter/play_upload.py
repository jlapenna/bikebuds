#!/usr/bin/env python
#
# Copyright 2014 Marta Rodriguez.
#
# Licensed under the Apache License, Version 2.0 (the 'License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Uploads an apk."""

import sys

import argparse
import httplib2
import json

from oauth2client.service_account import ServiceAccountCredentials
from oauth2client.client import AccessTokenRefreshError
from apiclient.discovery import build

def upload(package, service, apk, track):
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      service, ['https://www.googleapis.com/auth/androidpublisher'])

  http_auth = credentials.authorize(http=httplib2.Http())
  service = build('androidpublisher', 'v2', http=http_auth)

  try:
    edit_request = service.edits().insert(body={}, packageName=package)
    result = edit_request.execute()
    edit_id = result['id']

    apk_response = service.edits().apks().upload(
        editId=edit_id,
        packageName=package,
        media_body=apk).execute()

    print 'Version code %d has been uploaded' % apk_response['versionCode']

    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=track,
        packageName=package,
        body={u'versionCodes': [apk_response['versionCode']]}).execute()

    print 'Track %s is set for version code(s) %s' % (
        track_response['track'], str(track_response['versionCodes']))

    commit_request = service.edits().commit(
        editId=edit_id, packageName=package).execute()

    print 'Edit "%s" has been committed' % (commit_request['id'])

  except AccessTokenRefreshError, e:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')
    raise e

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--package', required=True, help='The package name. Example: com.android.sample')
  parser.add_argument('-s', '--service', required=True, help='The service account json file.')
  parser.add_argument('-a', '--apk', required=True, help='The path to the APK file to upload.')
  parser.add_argument('-t', '--track', choices=['alpha', 'beta', 'production','rollout'], default='alpha')
  args = parser.parse_args()

  upload(args.package, args.service, args.apk, args.track)

if __name__ == "__main__":
  main()
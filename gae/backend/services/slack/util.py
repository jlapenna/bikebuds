# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import urllib

from shared.config import config


_STRAVA_APP_LINK_REGEX = re.compile('(https://www.strava.com/([^/]+)/[0-9]+)')


def get_id(url):
    url = urllib.parse.urlparse(url)
    return int(url.path.split('/')[-1])


def generate_url(source):
    url = 'https://maps.googleapis.com/maps/api/staticmap?'
    params = {
        'key': config.firebase_app_config['apiKey'],
        'size': '512x512',
        'maptype': 'roadmap',
        'format': 'jpg',
    }

    summary_polyline = source.get('map', {}).get('summary_polyline')
    if summary_polyline:
        params['path'] = 'enc:%s' % (summary_polyline,)
    return url + urllib.parse.urlencode(params)

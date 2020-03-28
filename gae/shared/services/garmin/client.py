# Copyright 2020 Google LLC, Stanislav Khrapov
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

"""
"""

import json
import logging
import re

from functools import wraps

import requests

from shared.datastore.service import Service


URL_SSO_LOGIN = "https://sso.garmin.com/sso/signin"

URL_BASE = 'https://connect.garmin.com'
URL_MODERN = URL_BASE + '/modern'
URL_ACTIVITIES = URL_MODERN + '/proxy/usersummary-service/usersummary/daily/'
URL_HEARTRATES = URL_MODERN + '/proxy/wellness-service/wellness/dailyHeartRate/'
URL_BODY_COMPOSITION = URL_MODERN + '/proxy/weight-service/weight/daterangesnapshot'
URL_LEGACY_SESSION = URL_BASE + '/legacy/_session'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        + 'AppleWebKit/537.36 (KHTML, like Gecko) '
        + 'Chrome/79.0.3945.88 Safari/537.36'
    ),
    'origin': 'https://sso.garmin.com',
}


class Error(Exception):
    pass


class SessionExpiredError(Error):
    pass


def create(service):
    if not Service.has_credentials(service, required_key='password'):
        raise Exception('Cannot create Garmin client without creds: %s' % (service,))
    creds = service.get('credentials', {})
    session_state = creds.get('session_state')

    def refresh_callback(session_state):
        logging.debug('Garmin creds refresh for: %s', service.key)
        Service.update_credentials(service, {'session_state': session_state})

    garmin = Garmin(
        creds['username'], creds['password'], refresh_callback=refresh_callback
    )
    if session_state:
        garmin.set_session_state(**session_state)
    return garmin


def require_session(client_function):
    @wraps(client_function)
    def check_session(*args, **kwargs):
        client_object = args[0]
        if not (client_object._session and client_object.profile):
            logging.debug('No session established. Logging in.')
            client_object.login()
        try:
            return client_function(*args, **kwargs)
        except SessionExpiredError:
            client_object.login()
            return client_function(*args, **kwargs)

    return check_session


class Garmin(object):
    def __init__(self, username, password, refresh_callback=None):
        self._username = username
        self._password = password
        self._refresh_callback = refresh_callback

        self._session = None
        self._preferences = None

        self.profile = None

    def set_session_state(self, cookies=None, profile=None, preferences=None):
        if cookies or profile or preferences:
            if not (cookies and profile and preferences):
                raise ValueError('Must pass all or nothing.')
        self._session = requests.Session()
        self._session.headers.update(HEADERS)
        if cookies:
            self._session.cookies.update(cookies)
            self._preferences = preferences

            self.profile = profile

    def get_session_state(self):
        if not self._session:
            return None
        return {
            'cookies': self._session.cookies.get_dict(),
            'preferences': self._preferences,
            'profile': self.profile,
        }

    def login(self):
        logging.debug('Login...')
        self.set_session_state()
        try:
            self._authenticate()
        except Exception as err:
            # Clear the session.
            self.set_session_state()
            logging.debug('Clearing session and raising.')
            raise err
        finally:
            logging.debug('Finally calling refresh_callback.')
            if self._refresh_callback:
                self._refresh_callback(self.get_session_state())
        logging.debug('Login complete')

    def _authenticate(self):
        params = {
            # 'webhost': URL_BASE,
            'service': URL_MODERN,
            # 'source': URL_SSO_LOGIN,
            # 'redirectAfterAccountLoginUrl': URL_MODERN,
            # 'redirectAfterAccountCreationUrl': URL_MODERN,
            # 'gauthHost': URL_SSO_LOGIN,
            # 'locale': 'en_US',
            # 'id': 'gauth-widget',
            # 'cssUrl': 'https://static.garmincdn.com/com.garmin.connect/ui/css/gauth-custom-v1.2-min.css',
            # 'clientId': 'GarminConnect',
            # 'rememberMeShown': 'true',
            # 'rememberMeChecked': 'false',
            # 'createAccountShown': 'true',
            # 'openCreateAccount': 'false',
            # 'usernameShown': 'false',
            # 'displayNameShown': 'false',
            # 'consumeServiceTicket': 'false',
            # 'initialFocus': 'true',
            # 'embedWidget': 'false',
            # 'generateExtraServiceTicket': 'false',
        }

        data = {
            'username': self._username,
            'password': self._password,
            'embed': 'false',
            # 'lt': 'e1s1',
            # '_eventId': 'submit',
            # 'displayNameRequired': 'false',
        }

        logging.debug("Login to Garmin Connect using POST url %s", URL_SSO_LOGIN)
        login_response = self._session.post(URL_SSO_LOGIN, params=params, data=data)
        login_response.raise_for_status()

        logging.debug("Extracting auth ticket url")
        auth_ticket_url = self._extract_auth_ticket_url(login_response.text)
        logging.debug("Extracted auth ticket url: %s", auth_ticket_url)

        logging.info("claiming auth ticket ...")
        auth_response = self._session.get(auth_ticket_url)
        auth_response.raise_for_status()

        # There is auth info in here needed in order to fetch other services.
        self._preferences = self._extract_json(
            auth_response.text, 'VIEWER_USERPREFERENCES'
        )
        self.profile = self._extract_json(auth_response.text, 'SOCIAL_PROFILE')

        # some form of legacy _session. otherwise certain downloads will fail.
        self._session.get(URL_LEGACY_SESSION)
        auth_response.raise_for_status()

    @staticmethod
    def _extract_json(html, key):
        """Find and return json data."""
        found = re.search(key + r" = JSON.parse\(\"(.*)\"\);", html, re.M)
        if found:
            text = found.group(1).replace('\\"', '"')
            return json.loads(text)

    @staticmethod
    def _extract_auth_ticket_url(auth_response):
        """Extracts an authentication ticket URL from the response of an
        authentication form submission. The auth ticket URL is typically
        of form:
          https://connect.garmin.com/modern?ticket=ST-0123456-aBCDefgh1iJkLmN5opQ9R-cas
        :param auth_response: HTML response from an auth form submission.
        """
        match = re.search(r'response_url\s*=\s*"(https:[^"]+)"', auth_response)
        if not match:
            raise RuntimeError(
                "auth failure: unable to extract auth ticket URL. did you provide a correct username/password?"
            )
        auth_ticket_url = match.group(1).replace("\\", "")
        return auth_ticket_url

    @require_session
    def get_body_comp(self, start_date, end_date=None):  # 'YYY-mm-dd'
        end_date = end_date if end_date else start_date
        url = URL_BODY_COMPOSITION + '?startDate=' + start_date + '&endDate=' + end_date
        return self._get(url)

    @require_session
    def get_stats(self, start_date):  # cDate = 'YYY-mm-dd'
        url = (
            URL_ACTIVITIES
            + self.profile['displayName']
            + '?'
            + 'calendarDate='
            + start_date
        )
        return self._get(url)

    def _get(self, url):
        logging.debug("Fetching: %s", url)
        response = self._session.get(url)
        logging.debug(
            "Response code %s, and json %s", response.status_code, response.json(),
        )
        response.raise_for_status()

        if response.json().get('privacyProtected'):
            raise SessionExpiredError('Login expired')

        return response.json()

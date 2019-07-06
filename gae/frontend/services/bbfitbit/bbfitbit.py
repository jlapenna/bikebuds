# Copyright 2018 Google LLC
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


import flask


import fitbit

from shared import auth_util
from shared import task_util
from shared.config import config
from shared.datastore.service import Service
from shared.datastore.user import User


SERVICE_NAME = 'fitbit'

module = flask.Blueprint(
    SERVICE_NAME, __name__, template_folder='templates', static_folder='static'
)


@module.route('/services/fitbit/init', methods=['GET', 'POST'])
@auth_util.claims_required
def init(claims):
    # Creates the service if it doesn't exist.
    user = User.get(claims)
    Service.get(SERVICE_NAME, parent=user.key)

    dest = flask.request.args.get('dest', '')
    return get_auth_url_response(dest)


@module.route('/services/fitbit/redirect', methods=['GET'])
# @cross_origin(origins=['https://www.fitbit.com'])
@auth_util.claims_required
def redirect(claims):
    user = User.get(claims)
    service = Service.get(SERVICE_NAME, parent=user.key)

    code = flask.request.args.get('code')
    dest = flask.request.args.get('dest', '')

    auth_client = fitbit.FitbitOauth2Client(
        client_id=config.fitbit_creds['client_id'],
        client_secret=config.fitbit_creds['client_secret'],
        redirect_uri=get_redirect_uri(dest),
    )
    creds = auth_client.fetch_access_token(code)

    Service.update_credentials(service, creds)

    task_util.sync_service(service)

    return flask.redirect('/services/redirect?dest=' + dest)


def get_redirect_uri(dest):
    return config.frontend_url + '/services/fitbit/redirect?dest=' + dest


def get_auth_url_response(dest):
    auth_client = fitbit.FitbitOauth2Client(
        config.fitbit_creds['client_id'],
        config.fitbit_creds['client_secret'],
        redirect_uri=get_redirect_uri(dest),
    )
    url, state = auth_client.authorize_token_url()
    if flask.request.method == 'POST':
        return flask.jsonify({'authorize_url': url})
    else:
        return flask.redirect(url)

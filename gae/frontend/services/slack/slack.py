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

import hmac
import logging
import time

import flask

from shared.config import config
from shared import responses


SERVICE_NAME = 'slack'

module = flask.Blueprint(
    SERVICE_NAME, __name__, template_folder='templates', static_folder='static'
)


@module.route('/services/slack/events', methods=['POST'])
def events_post():
    verify_request(flask.request)

    event_data = flask.request.get_json()

    event_type = event_data['type']
    if event_type != 'url_verification':
        return responses.OK_SUB_EVENT_UNKNOWN

    challenge = event_data['challenge']

    return flask.jsonify({'challenge': challenge})


@module.route('/services/slack/events-test', methods=['POST'])
def events_test_post():
    event_data = flask.request.get_json()
    logging.info('Received test event: %s', event_data)

    # https://api.slack.com/docs/verifying-requests-from-slack#verification_token_deprecation
    # This approach for verification is deprecated
    token = event_data['token']
    if token != config.slack_creds['verification_token']:
        logging.warning('Received test event with unknown token')

    challenge = event_data['challenge']

    return flask.jsonify({'challenge': challenge})


def verify_request(request):
    # From: https://api.slack.com/docs/verifying-requests-from-slack
    try:
        slack_signing_secret = config.slack_creds['signing_secret']
        request_body = request.get_data()
        timestamp = request.headers['X-Slack-Request-Timestamp']
        if abs(time.time() - timestamp) > 60 * 5:
            # The request timestamp is more than five minutes from local time.
            # It could be a replay attack, so let's ignore it.
            return
        sig_basestring = 'v0:' + timestamp + ':' + request_body
        my_signature = (
            'v0='
            + hmac.compute_hash_sha256(slack_signing_secret, sig_basestring).hexdigest()
        )
        slack_signature = request.headers['X-Slack-Signature']
        if not hmac.compare(my_signature, slack_signature):
            responses.abort(responses.INVALID_TOKEN)
    except Exception:
        responses.abort(responses.BAD_REQUEST)

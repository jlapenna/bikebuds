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


import logging

from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from shared import logging_util
from shared import responses
from shared.config import config

from admin import api as admin_api
from bikebuds import api as bikebuds_api
from models import api as models_api

app = Flask(__name__)
CORS(app, origins=config.cors_origins)

app.logger.setLevel(logging.DEBUG)
logging_util.debug_logging()
logging_util.silence_logs()

# https://flask-restplus.readthedocs.io/en/stable/swagger.html#documenting-authorizations
# https://cloud.google.com/endpoints/docs/openapi/authenticating-users-firebase#configuring_your_openapi_document
# fmt: off
authorizations = {
    'api_key': {'name': 'key', 'in': 'query', 'type': 'apiKey'},
    'firebase': {
        'authorizationUrl': '',
        'flow': 'implicit',
        'type': 'oauth2',
        'x-google-issuer': 'https://securetoken.google.com/' + config.project_id,
        'x-google-jwks_uri': 'https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com',
    },
}
# fmt: on

api = Api(
    app,
    version='1.0',
    title='Bikebuds APIs',
    security=list(authorizations.keys()),
    authorizations=authorizations,
    default='bikebuds',
)
api.add_namespace(admin_api)
api.add_namespace(bikebuds_api)
api.add_namespace(models_api)

app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_OPERATION_ID = True


@app.route('/_ah/warmup')
def warmup():
    return responses.OK


@app.before_request
def before():
    logging_util.before()


@app.after_request
def after(response):
    return logging_util.after(response)


if __name__ == '__main__':
    host, port = config.api_url[7:].split(':')
    app.run(host='localhost', port=port, debug=True)

#!/bin/bash
#
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

# Deploy the service to appengine, rewriting code to support production.

source gae/base.sh

function main() {
  local repo_path="$(get_repo_path)";

  # First we update the API endpoint.
  gcloud endpoints services deploy gae/api/bikebudsv1openapi.json

  sed -i "s#\"rootUrl\": .*#\"rootUrl\": \"https://api-dot-bikebuds-app.appspot.com/_ah/api/\",#" gae/api/bikebuds-v1.discovery
  sed -i "s#var backendHostUrl = .*#var backendHostUrl = 'https://backend-dot-bikebuds-app.appspot.com';#" gae/frontend/main.js
  yes|gcloud app deploy \
    gae/frontend/app.yaml \
    gae/backend/app.yaml \
    gae/index.yaml \
    ;
  sed -i "s#\"rootUrl\": .*#\"rootUrl\": \"http://localhost:8081/_ah/api/\",#" gae/api/bikebuds-v1.discovery
  sed -i "s#var backendHostUrl = .*#var backendHostUrl = 'http://localhost:8082';#" gae/frontend/main.js
}

main "$@"

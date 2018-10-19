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

# Run a local instance, rewriting code for local development.

source gae/base.sh

function main() {
  local repo_path="$(get_repo_path)";

  local env_path=$(readlink -f "$HOME/appengine_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Using virtual environment at ${env_path}"
  source "${env_path}/bin/activate"

  sed -i "s#\"rootUrl\": .*#\"rootUrl\": \"http://localhost:8081/_ah/api/\",#" gae/api/bikebuds-v1.discovery
  sed -i "s#var apiHostUrl = .*#var apiHostUrl = 'http://localhost:8081';#" gae/frontend/main.js
  sed -i "s#var backendHostUrl = .*#var backendHostUrl = 'http://localhost:8082';#" gae/frontend/main.js

  dev_appserver.py \
    gae/frontend/app.yaml \
    gae/api/app.yaml \
    gae/backend/app.yaml \
    ;
}

main "$@"

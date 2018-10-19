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

# Do development in the backend gae environment.

source gae/base.sh

function main() {
  local repo_path="$(get_repo_path)";

  local api_path="${repo_path}/gae/api"
  local backend_path="${repo_path}/gae/backend"
  local frontend_path="${repo_path}/gae/frontend"

  local env_path=$(readlink -f "$HOME/standalone_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Using virtual environment at ${env_path}"
  source "${env_path}/bin/activate"

  sed -i "s/var apiHostUrl = .*/var apiHostUrl = 'http:\/\/localhost:8081';/" gae/frontend/main.js
  sed -i "s/var backendHostUrl = .*/var backendHostUrl = 'http:\/\/localhost:8082';/" gae/frontend/main.js

  cd gae/backend;

  ipython -i "$1"
}

main "$@"


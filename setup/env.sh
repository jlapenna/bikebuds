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

# Configures an environment to run the backend in.

source setup/base.sh

function main() {
  local repo_path="$(get_repo_path)";

  activate_env

  local api_path="${repo_path}/gae/api"
  local backend_path="${repo_path}/gae/backend"
  local frontend_path="${repo_path}/gae/frontend"

  echo ""
  echo "Installing frontend dependencies."
  rm -rf "${frontend_path}/lib"
  pip2 install -t "${frontend_path}/lib" -r "${frontend_path}/requirements.txt"

  echo ""
  echo "Copying over service keys to frontend."
  cp -rf "${repo_path}/private/service_keys" "${frontend_path}/lib/"

  echo ""
  echo "Installing api dependencies."
  rm -rf "${api_path}/lib"
  pip2 install -t "${api_path}/lib" -r "${api_path}/requirements.txt"

  echo ""
  echo "Copying over service keys to api."
  cp -rf "${repo_path}/private/service_keys" "${api_path}/lib/"

  echo ""
  echo "Installing backend dependencies."
  rm -rf "${backend_path}/lib"
  pip2 install -t "${backend_path}/lib" -r "${backend_path}/requirements.txt"

  echo ""
  echo "Copying over service keys to backend."
  cp -rf "${repo_path}/private/service_keys" "${backend_path}/lib/"

  echo ""
  echo "Initializing npm packages for frontend."
  pushd gae/frontend
  npm install
  popd
}

main "$@"

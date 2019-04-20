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

source tools/scripts/base.sh

function main() {
  local repo_path="$(get_repo_path)";

  activate_virtualenv

  echo ""
  echo "Setting up environments."
  mkdir environments >/dev/null 2>&1;
  pushd environments;
  if [[ ! -d "dev" ]]; then
    echo "TODO: Please install the dev config git repo, then press enter."
    echo "cd ${repo_path}/environments"
    echo "gcloud --project=bikebuds-test source repos clone env dev"
    read
  fi
  if [[ ! -d "prod" ]]; then
    echo "TODO: Please install the prod config git repo, then press enter."
    echo "cd ${repo_path}/environments;"
    echo "gcloud --project=bikebuds-app source repos clone env prod"
    read
  fi
  popd

  echo ""
  echo "Installing frontend dependencies."
  local frontend_path="${repo_path}/gae/frontend"
  rm -rf "${frontend_path}/lib"
  pip2 install -t "${frontend_path}/lib" -r "${frontend_path}/requirements.txt"
  pushd "$frontend_path/lib"
  ln -sf ../../../environments/env
  popd

  echo ""
  echo "Installing api dependencies."
  local api_path="${repo_path}/gae/api"
  rm -rf "${api_path}/lib"
  pip2 install -t "${api_path}/lib" -r "${api_path}/requirements.txt"
  pushd "$api_path/lib"
  ln -sf ../../../environments/env
  popd

  echo ""
  echo "Installing backend dependencies."
  local backend_path="${repo_path}/gae/backend"
  rm -rf "${backend_path}/lib"
  pip2 install -t "${backend_path}/lib" -r "${backend_path}/requirements.txt"
  pushd "$backend_path/lib"
  ln -sf ../../../environments/env
  popd

  echo ""
  echo "Initializing npm packages for frontend."
  pushd gae/frontend
  npm install
  popd
}

main "$@"

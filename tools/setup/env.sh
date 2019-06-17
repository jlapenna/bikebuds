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

  echo ""
  echo "Setting up virtual environments."
  mkdir environments >/dev/null 2>&1;
  mkdir environments/virtual/client >/dev/null 2>&1;
  mkdir environments/virtual/gae >/dev/null 2>&1;
  mkdir environments/virtual/gae3 >/dev/null 2>&1;

  echo ""
  echo "Installing libraries into 'gae' virtualenv."
  activate_virtualenv gae python2
  pip2 install ipython inotify
  deactivate

  echo ""
  echo "Setting up config environments."
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
  echo "Setting up frontend."
  local frontend_path="${repo_path}/gae/frontend"

  echo ""
  echo "Setting up api."
  local api_path="${repo_path}/gae/api"

  echo ""
  echo "Setting up backend."
  local backend_path="${repo_path}/gae/backend"

  echo ""
  echo "Initializing npm packages for frontend."
  pushd gae/frontend
  HUSKY_SKIP_INSTALL=true npm install
  popd
}

main "$@"

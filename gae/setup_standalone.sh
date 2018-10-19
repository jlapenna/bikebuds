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

# Configures an environment to mess around with, one that looks similar to the
# gae standard environment.
#
# ./gae/setup_standalone.sh

function main() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename $repo_path)" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo."
    exit 1;
  fi
  local backend_path="${repo_path}/gae/backend"

  local env_path=$(readlink -f "$HOME/standalone_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Setting up environment for standalone dev..."
  echo ""
  echo "Setting up virtual environment at ${env_path}"
  virtualenv --python python2 "${env_path}"
  source "${env_path}/bin/activate"

  echo ""
  echo "Installing backend dependencies."
  pip install -r "${backend_path}/requirements.txt"

  echo ""
  echo "Installing other useful things."
  pip install ipython
}

main "$@"

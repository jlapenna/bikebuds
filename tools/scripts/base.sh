#!/bin/bash
#
# Copyright 2019 Google LLC
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

PROD_API_HOSTNAME='api.bikebuds.cc'
LOCAL_API_HOSTNAME='localhost:8082'

function load_config() {
  for kv in $(jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' environments/env/config.json); do
    export "CONFIG_${kv}";
  done;
}

function verify_deps() {
  for dep in "${@}"; do 
    if [[ ! "$(command -v $dep)" ]]; then
      echo "Error: $dep is not installed. Quitting." >&2
      exit 1
    fi
  done
}

function get_repo_path() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename ${repo_path})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo. Quitting." >&2
    exit 1;
  fi
  echo "${repo_path}";
}

function set_dev_environment() {
  echo "Activating dev environment."
  pushd environments
  rm env
  ln -sf dev env
  popd
}

function set_prod_environment() {
  echo "Activating prod environment."
  pushd environments
  rm env
  ln -sf prod env
  popd
}


function get_client_virtualenv_path() {
  local env_path=$(readlink -e "$(get_repo_path)/client_env")
  if [[ ! -e "$env_path" ]]; then
    echo "Unable to locate the virtual environment. Quitting." >&2
    exit 1;
  fi
  echo "${env_path}";
}

function activate_client_virtualenv() {
  local env_path="$(get_client_virtualenv_path)";
  echo "Activating virtual environment at ${env_path}"
  virtualenv --python python3 "${env_path}" >/dev/null 2>&1
  source "${env_path}/bin/activate"
  if [ "$?" -ne 0 ]; then
    echo "Unable to setup virtual environment. Quitting." >&2
    exit 2;
  fi
}

function get_gae_virtualenv_path() {
  local env_path=$(readlink -e "$(get_repo_path)/appengine_env")
  if [[ ! -e "$env_path" ]]; then
    echo "Unable to locate the virtual environment. Quitting." >&2
    exit 1;
  fi
  echo "${env_path}";
}

function activate_gae_virtualenv() {
  local env_path="$(get_gae_virtualenv_path)";
  echo "Activating virtual environment at ${env_path}"
  virtualenv --python python2 "${env_path}" >/dev/null 2>&1
  source "${env_path}/bin/activate"
  if [ "$?" -ne 0 ]; then
    echo "Unable to setup virtual environment. Quitting." >&2
    exit 2;
  fi
}

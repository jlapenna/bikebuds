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
      echo "Error: $dep is not installed." >&2
      return 1
    fi
  done
}

function get_repo_path() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename ${repo_path})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo." >&2
    return 1;
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

function activate_virtualenv() {
  local env_name="$1"
  local python="$2"
  local env_path=$(readlink -f "$(get_repo_path)/environments/virtual/${env_name}")

  #echo "Installing virtual environment at ${env_path}"
  #virtualenv --python "${python}" "${env_path}"
  
  echo "Activating virtual environment at ${env_path}"
  source "${env_path}/bin/activate"
  if [ "$?" -ne 0 ]; then
    echo "Unable to setup virtual environment." >&2
    return 2;
  fi
}

function activate_client_virtualenv() {
  activate_virtualenv client python3
  return $?
}

function activate_gae_virtualenv() {
  activate_virtualenv gae python2
  return $?
}

function activate_gae3_virtualenv() {
  activate_virtualenv gae3 python3
  return $?
}

function setup_datastore_emulator() {
  load_config
  echo "Running against the local datastore.";
  export DATASTORE_EMULATOR_HOST="${CONFIG_datastore_emulator_host}";
  export DATASTORE_PROJECT_ID="${CONFIG_project_id}";
  export DATASTORE_DATASET="${CONFIG_project_id}";
  export DATASTORE_EMULATOR_HOST_PATH=${CONFIG_datastore_emulator_host}/datastore
  export DATASTORE_HOST=${CONFIG_datastore_emulator_host}
  export DATASTORE_PORT="$(echo ${CONFIG_datastore_emulator_host} | cut -d':' -f2)"
}

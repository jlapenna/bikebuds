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
  local env=${BIKEBUDS_ENV}
  if [[ "${env}" == "" ]]; then
    env="environments/env"
  fi
  config="${env}/config.json";

  for kv in $(jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' ${config}); do
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
  local repo_path=$(readlink -m "$PWD")
  echo "${repo_path}";
  if [[ "$(basename ${repo_path})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo!" >&2
    return 1;
  fi
}

function get_virtualenv_path() {
  local env_name="$1"
  local env_path=$(readlink -m "$(get_repo_path)/virtualenv/${env_name}")
  echo "${env_path}";
  if [ ! -d "${env_path}" ]; then
    return 1;
  fi
}

function set_dev_environment() {
  echo "Activating dev environment."
  pushd environments
  rm env
  ln -sf dev env
  popd

  echo "Wiping flutter build cache."
  rm -rf flutter/build/
}

function set_prod_environment() {
  echo "Activating prod environment."
  pushd environments
  rm env
  ln -sf prod env
  popd

  echo "Wiping flutter build cache."
  rm -rf flutter/build/
}

function activate_virtualenv() {
  local env_name="$1"
  local python="$2"
  local env_path="$(get_virtualenv_path "${env_name}")"

  if [ ! -d "${env_path}" ]; then
    echo "Unable to find virtual environment, creating it at ${env_path}." >&2
    virtualenv --python "${python}" "${env_path}";
    if [ "$?" -ne 0 ]; then
      echo "Unable to create virtual environment." >&2
      return 2;
    fi
  fi
  
  echo "Activating virtual environment at ${env_path}"
  source "${env_path}/bin/activate"
  if [ "$?" -ne 0 ]; then
    echo "Unable to activate virtual environment." >&2
    return 2;
  fi
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

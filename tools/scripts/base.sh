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


function set_bikebuds_path() {
  if [[ "${BIKEBUDS_PATH}" != "" ]]; then
    return 0;
  fi

  local readlink_pwd="$(readlink -m "$PWD")"
  if [[ "$(basename ${readlink_pwd})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo!" >&2
    return 1;
  fi
  export BIKEBUDS_PATH="${readlink_pwd}"
}

function verify_bikebuds_path() {
  local readlink_pwd="$(readlink -m "$PWD")"
  if [[ "$(basename ${readlink_pwd})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo!" >&2
    exit 1;
  fi
}

function load_config() {
  set_bikebuds_path

  local bikebuds_env="environments/env";
  local config="${bikebuds_env}/config.json";

  for kv in $(jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' ${config}); do
    export "CONFIG_${kv}";
  done;
}

function get_virtualenv_path() {
  local env_name="$1"
  local env_path=$(readlink -m "${BIKEBUDS_PATH}/virtualenv/${env_name}")
  echo "${env_path}";
  if [ ! -d "${env_path}" ]; then
    return 1;
  fi
}

function set_dev_environment() {
  echo "Activating dev environment."
  local current_env="$(basename $(realpath environments/env))"
  if [[ "$current_env" != "dev" ]]; then
    pushd environments
    rm env
    ln -sf dev env
    popd

    echo "Wiping flutter build cache."
    pushd flutter;
    flutter clean;
    popd;
  fi;
}

function set_prod_environment() {
  echo "Activating prod environment."
  local current_env="$(basename $(realpath environments/env))"
  if [[ "$current_env" != "prod" ]]; then
    pushd environments
    rm env
    ln -sf prod env
    popd

    echo "Wiping flutter build cache."
    pushd flutter;
    flutter clean;
    popd;
  fi;
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

verify_bikebuds_path
set_bikebuds_path

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

# Dependencies for development, in order to start a dev server, for example.

source tools/scripts/base.sh

export REPO_PATH="$(get_repo_path)";

export FCM_SERVER_KEY="$(jq -r '.["server_key"]' environments/env/service_keys/firebase-messaging.json)"
export FCM_PROD_SERVER_KEY="$(jq -r '.["server_key"]' environments/prod/service_keys/firebase-messaging.json)"
export FCM_DEV_SERVER_KEY="$(jq -r '.["server_key"]' environments/dev/service_keys/firebase-messaging.json)"

function source_files() {
  find . \
    \( \
    -path "./$(realpath --relative-to=. $REPO_PATH/virtualenv)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/flutter/build)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/flutter/.dart_tool)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/api/lib)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/backend/lib)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/client/lib)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/frontend/build)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/frontend/lib)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/frontend/node_modules)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/frontend/package-lock.json)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/generated)" \
    \) -prune \
    -o \( \
        -name '*.sh' \
        -o -name '*.dart'  \
        -o -name '*.java'  \
        -o -name '*.js' \
        -o -name '*.jsx' \
        -o -name '*.py' \
        -o -name '*.json' \
    \) -type f -print \
    ;

}

function config_files() {
  find . \
    \( \
    -path "./$(realpath --relative-to=. $REPO_PATH/virtualenv)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/flutter/build)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/flutter/.dart_tool)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/api/lib)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/backend/lib)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/client/lib)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/frontend/build)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/frontend/lib)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/gae/frontend/node_modules)" -o \
    -path "./$(realpath --relative-to=. $REPO_PATH/generated)" \
    \) -prune \
    -o \( \
        -name '*.yaml' \
        -o -name '*requirements*txt' \
        -o -name '*.json' \
        -o -name '*.txt' \
    \) -type f -print \
    ;

}

function cgrep() {
  egrep "$@" $(config_files)
}

function sgrep() {
  egrep "$@" $(source_files)
}

function watch_logs() {
  local service=$1;
  local version=$2;

  local version_flag=""
  if [[ "${version}" == "latest" ]]; then
    local latest="$(gcloud --project=bikebuds-app app versions list \
        --service ${service} --sort-by '~version' \
        --filter="traffic_split=1.0" --format='value(id)')"
    version_flag="-v ${latest}"
  elif [[ "${version}" != "" ]]; then
    version_flag="-v ${version}"
  fi

  xtitle logs: $service;

  if [[ "${service}" == "frontend" ]]; then
    service="default";
  fi
  gcloud --project=bikebuds-app app logs tail -s "${service}" ${version_flag}
}

activate_virtualenv dev python3

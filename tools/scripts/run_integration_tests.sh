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

source tools/scripts/base.sh || exit 1

function main() {
  local client_path="${BIKEBUDS_PATH}/gae/client"

  activate_virtualenv integration python3
  pip -q install -r ${client_path}/requirements.txt
  pip -q install -r ${client_path}/requirements_test_integration.txt

  load_config

  if [[ "" != "${CONFIG_datastore_emulator_host}" ]]; then
    echo "Running against the local datastore.";
    export DATASTORE_EMULATOR_HOST="${CONFIG_datastore_emulator_host}";
    export DATASTORE_PROJECT_ID="${CONFIG_project_id}";
    export DATASTORE_EMULATOR_HOST_PATH=${EMULATOR_HOST}/datastore
    export DATASTORE_HOST=${EMULATOR_HOST}
  fi

  python -m unittest discover -s "${client_path}"
  result=$?;

  deactivate

  exit ${result};
}

main "$@"

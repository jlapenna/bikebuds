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

# Run a local instance, rewriting code for local development.

set -e

source tools/scripts/base.sh

function main() {
  local repo_path="$(get_repo_path)";

  activate_virtualenv dev_appserver python2
  pip install grpcio

  load_config;

  # We want our dev, not prod environment (generally a no-op).
  set_dev_environment

  # Ensure all client libs point to our local datastore.
  # Clients need this to know where to connect, but when specififed,
  # dev_appserver won't launch its own emulator...
  # export DATASTORE_EMULATOR_HOST="${CONFIG_datastore_emulator_host}";
  # Instead we're setting this within ds_util.py

  # The rest are okay as is.
  export DATASTORE_PROJECT_ID="${CONFIG_project_id}";
  export DATASTORE_DATASET="${CONFIG_project_id}";
  export DATASTORE_EMULATOR_HOST_PATH=${CONFIG_datastore_emulator_host}/datastore
  export DATASTORE_HOST=${CONFIG_datastore_emulator_host}
  export DATASTORE_PORT="$(echo ${CONFIG_datastore_emulator_host} | cut -d':' -f2)"

  # https://cloud.google.com/appengine/docs/standard/python3/testing-and-deploying-your-app
  # Suggests not using dev_appserver.py -- it remains to be seen how to do task
  # queues, for example. See the other local_*.sh files for an attempt to use
  # "standard tools"


  # https://cloud.google.com/appengine/docs/standard/python3/testing-and-deploying-your-app#local-dev-server
  # Describes support for dev_appserver contrary to earlier in that same page...
  dev_appserver.py \
    -A $CONFIG_project_id \
    --log_level=debug \
    --support_datastore_emulator=1 \
    --datastore_emulator_port=${DATASTORE_PORT} \
    --specified_service_ports=default:8081,api:8082,backend:8083 \
    --addn_host="*.ngrok.io" \
    --env_var=FLASK_ENV=development \
    gae/frontend/app-local.yaml \
    gae/api/app.yaml \
    gae/backend/app-local.yaml \
    ;
    # --dev_appserver_log_level=debug \

  deactivate
}

main "$@"

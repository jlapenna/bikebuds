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

  deactivate 2>/dev/null || echo ""

  activate_virtualenv dev_appserver python2

  load_config;

  # We want our dev, not prod environment (generally a no-op).
  set_dev_environment

  export GOOGLE_APPLICATION_CREDENTIALS=environments/env/service_keys/appengine.json

  # Launch the datastore emulator
  gcloud beta emulators datastore start \
      --host-port="${CONFIG_datastore_emulator_host}" \
      --project "${CONFIG_project_id}" \
      &
  #    #--no-store-on-disk \

  # $(gcloud beta emulators datastore env-init)  # Could set these.
  export DATASTORE_DATASET="${CONFIG_project_id}"
  export DATASTORE_EMULATOR_HOST="${CONFIG_datastore_emulator_host}"
  export DATASTORE_EMULATOR_HOST_PATH="${CONFIG_datastore_emulator_host}/datastore"
  export DATASTORE_HOST="${CONFIG_datastore_emulator_host}"
  export DATASTORE_PROJECT_ID="${CONFIG_project_id}"

  # https://cloud.google.com/appengine/docs/standard/python3/testing-and-deploying-your-app#local-dev-server
  # Describes support for dev_appserver contrary to earlier in that same page...
  dev_appserver.py \
    -A "${CONFIG_project_id}" \
    --log_level=debug \
    --support_datastore_emulator=true \
    --running_datastore_emulator_host="${CONFIG_datastore_emulator_host}" \
    --specified_service_ports=default:8081,api:8082,backend:8083 \
    --addn_host="*.ngrok.io" \
    --env_var=FLASK_ENV=development \
    --env_var=OAUTHLIB_INSECURE_TRANSPORT=1 \
    --env_var=GOOGLE_APPLICATION_CREDENTIALS=environments/env/service_keys/appengine.json \
    --env_var=DATASTORE_DATASET="${CONFIG_project_id}" \
    --env_var=DATASTORE_EMULATOR_HOST="${CONFIG_datastore_emulator_host}" \
    --env_var=DATASTORE_EMULATOR_HOST_PATH="${CONFIG_datastore_emulator_host}/datastore" \
    --env_var=DATASTORE_HOST="${CONFIG_datastore_emulator_host}" \
    --env_var=DATASTORE_PROJECT_ID="${CONFIG_project_id}" \
    gae/frontend/app-local.yaml \
    gae/api/app.yaml \
    gae/backend/app-local.yaml \
    &
    #--appidentity_email_address="" \
    #--appidentity_private_key_path="" \
    # --dev_appserver_log_level=debug \

  pushd gae/frontend
  EDITOR=cat PORT=8080 BROWSER=none npm start | tee
  popd

  # Kill anything that's pending.
  kill $(jobs -p)

  $(gcloud beta emulators datastore env-unset)
  deactivate
}

main "$@"

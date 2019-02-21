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

source setup/base.sh

function main() {
  local repo_path="$(get_repo_path)";

  activate_virtualenv
  set_local_environment

  pushd gae/frontend;
  BROWSER=none npm start &
  popd

  dev_appserver.py \
    -A bikebuds-test \
    --log_level=debug \
    --enable_console \
    --specified_service_ports=default:8081,api:8082,backend:8083 \
    gae/frontend/app.yaml \
    gae/api/app.yaml \
    gae/backend/app.yaml \
    ;
  fg;
}

main "$@"

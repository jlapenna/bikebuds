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

# Configures an environment to run the backend in.

source tools/scripts/base.sh || exit 1

function main() {
  echo ""
  echo "Setting up config environments."
  pushd environments;
  if [[ ! -d "dev" ]]; then
    echo "TODO: Please install the dev config git repo, then press enter."
    echo "cd ${BIKEBUDS_PATH}/environments"
    echo "gcloud --project=bikebuds-test source repos clone env dev"
    read
  fi
  if [[ ! -d "prod" ]]; then
    echo "TODO: Please install the prod config git repo, then press enter."
    echo "cd ${BIKEBUDS_PATH}/environments;"
    echo "gcloud --project=bikebuds-app source repos clone env prod"
    read
  fi
  popd

  set_dev_environment
}

main "$@"

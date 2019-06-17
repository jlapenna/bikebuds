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

source tools/scripts/base.sh

export REPO_PATH="$(get_repo_path)";

function main() {
  local final_result=0;

  local services="frontend api backend";
  for service in ${services}; do
    local result=0;

    activate_virtualenv ${service} python3

    pushd gae/${service}
    pip install -r requirements.txt > /dev/null 2>&1
    result=$?;
    if [[ ${result} != 0 ]]; then
      echo "Unable to pip install. Aborting."
      exit 3;
    fi
    python -m unittest
    result=$?;
    popd

    deactivate

    if [[ ${result} != 0 ]]; then
      final_result=${result};
    fi
  done

  exit ${final_result};
}

main "$@"

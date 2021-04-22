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
load_config;

function main() {
  if [[ -z "$@" ]]; then
    local services="shared frontend api backend";
  else
    local services="$@";
  fi

  local final_result=0;
  for service in ${services}; do
    local result=0;

    activate_virtualenv ${service} python3

    pushd gae/${service}
    pip -q install -r requirements.txt
    result=$?;
    if [[ ${result} != 0 ]]; then
      echo "Unable to pip install. Aborting."
      exit 3;
    fi

    if [ -e "test_requirements.txt" ]; then
      pip -q install -r test_requirements.txt
      result=$?;
      if [[ ${result} != 0 ]]; then
        echo "Unable to pip install test_requirements.txt. Aborting."
        exit 3;
      fi
    fi

    export GOOGLE_APPLICATION_CREDENTIALS=environments/env/service_keys/appengine.json
    export PYTHONPATH="$PYTHONPATH:$BIKEBUDS_REPO/gae"

    python -m unittest discover
    result=$?;
    echo '================================================================================'
    popd

    deactivate

    if [[ ${result} != 0 ]]; then
      final_result=${result};
    fi
  done

  if [[ ${final_result} != 0 ]]; then
    echo ""
    echo "SOME TESTS FAILED, SEE ABOVE!";
  fi
  exit ${final_result};
}

main "$@"

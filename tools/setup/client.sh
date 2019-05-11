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

# Dependencies for development, in order to start a dev server, for example.

source tools/scripts/base.sh


function main() {
  local repo_path="$(get_repo_path)";
  local client_path="${repo_path}/gae/client"

  echo ""
  echo "Installing client dependencies."
  activate_client_virtualenv
  pip3 install -r "${client_path}/requirements.txt"
  deactivate

  echo ""
  echo "Linking environments."
  rm -rf "${client_path}/lib"
  mkdir "${client_path}/lib"
  pushd "$client_path/lib"
  ln -sf ../../../environments/env
  popd
}

main "$@"

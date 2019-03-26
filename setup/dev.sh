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

source setup/base.sh

function main() {
  local repo_path="$(get_repo_path_no_verify)";

  sudo apt install -y python python-dev python-pip
  sudo apt install -y python3 python3-dev
  sudo apt install -y virtualenv
  sudo apt install -y gradle
  sudo apt install -y google-cloud-sdk-app-engine-python \
      google-cloud-sdk-app-engine-python-extras google-cloud-sdk-datastore-emulator

  echo "Apt installed python2.7, pip 2.x, virtualenv, gradle and gcloud cli."
  echo "Or it didn't, you might need to install them yourself. Press enter."
  read

  echo "Install flutter in ~/flutter/sdk, then press enter."
  read

  echo "Install android studio (and the sdk in ~/android/sdk), then press enter."
  read

  echo "Install NPM, then press enter."
  read
  npm install -g firebase-tools
  npm install -g fcm-cli

  echo "Now make sure dart, flutter, and android tools are in your path, then press enter."
  read

  echo "Run setup/discapis.sh, after ensuring your path is set up correctly."
}

main "$@"

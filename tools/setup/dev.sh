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

source tools/scripts/base.sh || exit 1

function main() {
  echo "Installing the correct packages with apt"
  sudo apt install -y python3 python3-dev python3-pip python3-virtualenv python3-venv
  sudo apt install -y virtualenv
  sudo apt install -y gradle
  sudo apt install -y python2.7 python2.7-dev  # required by dev_appserver.py
  sudo apt install -y google-cloud-sdk-app-engine-python \
      google-cloud-sdk-app-engine-python-extras google-cloud-sdk-datastore-emulator
  sudo apt install -y jq

  echo "Installing the firebase CLI"
  curl -sL https://firebase.tools | bash

  echo "Apt installed a few libraries."
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

  echo "Now make sure ngrok is installed and authenticated, then press enter."
  read

  echo "Downloading an openapi-generator for dart."
  git clone https://github.com/openapitools/openapi-generator generated/openapi-generator
  pushd generated/openapi-generator
  mvn clean package
  popd

  echo "Initializing npm packages for frontend."
  pushd gae/frontend
  npm install
  popd

  echo "Initializing dev shell requirements."
  activate_virtualenv dev python3
  pip3 install -r tools/setup/dev_requirements.txt

  echo "Initializing pre-commit."
  pre-commit install

  deactivate
  echo "Finished initializing dev shell requirements."

  echo "Initializing dev_appserver environment."
  activate_virtualenv "dev_appserver" "python2.7";
  pip install grpcio;
  deactivate

  echo "Finished setting up shell requirements."
}

main "$@"

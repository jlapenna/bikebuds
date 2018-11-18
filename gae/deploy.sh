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

# Deploy the service to appengine, rewriting code to support production.

source setup/base.sh

function main() {
  local repo_path="$(get_repo_path)";
  local services="frontend api backend";

  local env_path=$(readlink -f "${repo_path}/appengine_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment."
    exit 1;
  fi
  source "${env_path}/bin/activate"

  # First, commit all the code outstanding into a temporary commit for
  # safe-keeping.
  git add .
  git commit --allow-empty -a -m"Deploy Commit: $(date)";
  local committed="$?";

  ./gae/update_api.sh

  # First, update the API endpoint.
  gcloud endpoints services deploy gae/api/bikebudsv1openapi.json

  # Then, build the react app.
  pushd gae/frontend
  npm run build
  popd

  # Appengine no longer supports symlinks when uploading an app.
  # We have to manually copy over files before deploying, then restore the
  # links.
  # https://issuetracker.google.com/issues/70571662

  for service in ${services}; do
    rm "gae/${service}/shared";
    cp -r "gae/shared" "gae/${service}/"
  done;

  # Then, deploy everything.
  yes|gcloud app deploy \
    gae/cron.yaml \
    $(for service in ${services}; do echo gae/${service}/app.yaml; done) \
    ;

  # Then restore everything
  git clean -fd
  git reset --hard HEAD

  # And reset the state of the client to before the deploy-commit.
  if [ "$committed" -eq 0 ]; then
    git reset HEAD~
  fi;
}

main "$@"

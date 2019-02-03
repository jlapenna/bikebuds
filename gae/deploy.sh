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

# Using the same version results in app caching and inconsistent new release
# deployments.
#VERSION=10000

function main() {
  local repo_path="$(get_repo_path)";

  activate_env

  if [[ -z "$@" ]]; then
    local services="frontend api backend";
  else
    local services="$@";
  fi

  local date="$(date)";
  # First, commit all the code outstanding into a temporary commit for
  # safe-keeping.
  git add .
  git commit --allow-empty -a -m"Working Set: ${date}";

  # Make sure that all our code talks to a prod instance, (don't pass "local").
  ./gae/update_api.sh

  if [[ "$services" == *"api"* ]]; then
    # First, update the API endpoint.
    gcloud endpoints services deploy gae/api/bikebudsv1openapi.json
  fi;

  if [[ "$services" == *"frontend"* ]]; then
    # Maybe build the react app.
    pushd gae/frontend
    npm run build
    popd
  fi

  # Appengine no longer supports symlinks when uploading an app.
  # We have to manually copy over files before deploying, then restore the
  # links.
  # https://issuetracker.google.com/issues/70571662
  # Actually, this is fixed, now...
  #for service in ${services}; do
  #  rm "gae/${service}/shared";
  #  cp -r "gae/shared" "gae/${service}/"
  #done;

  # In order to include /lib/ in our uploaded source, we need to manipulate the
  # gae gitignore to strip it right before upload
  sed -i '/\/lib/d' gae/.gitignore
  git add . >/dev/null
  git commit --allow-empty -a -m"Include lib: ${date}" >/dev/null

  # Then, deploy everything.
  yes|gcloud app deploy \
    gae/frontend/cron.yaml \
    gae/frontend/index.yaml \
    $(for service in ${services}; do echo gae/${service}/app.yaml; done) \
    ;

  git push --force production master

  # Break apart the include lib commit.
  git reset HEAD~

  # And then check that out, effectively reverting to the working set.
  git checkout .

  # Finally break apart the working set commit, back to where we started before
  # the deploy script.
  git reset HEAD~
}

main "$@"

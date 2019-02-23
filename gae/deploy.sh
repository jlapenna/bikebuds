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

function delete_old_versions() {
  # From: https://almcc.me/blog/2017/05/04/removing-older-versions-on-google-app-engine/
  local service=$1
  local max_versions=$2

  local versions=$(gcloud app versions list --service default --sort-by '~version' --filter="version.servingStatus='STOPPED'" --format 'value(version.id)' | sort -r)
  local count=0
  echo "Keeping the $max_versions latest versions of the $1 service"
  for version in $versions; do
    ((count++))
    if [ $count -gt $max_versions ]; then
      echo "Going to delete version $version of the $service service."
      gcloud app versions delete $version --service $service -q
    else
      echo "Going to keep version $version of the $service service."
    fi
  done
}

function main() {
  local repo_path="$(get_repo_path)";

  activate_virtualenv
  set_prod_environment

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

  # Make sure we're not using cached pyc.
  find ./ -iname '*.py[co]' -delete

  if [[ "$services" == *"frontend"* ]]; then
    # Maybe build the react app.
    pushd gae/frontend
    npm run build
    popd
  fi

  # In order to include /lib/ in our uploaded source, we need to manipulate the
  # gae gitignore to strip it right before upload
  sed -i '/\/lib/d' gae/.gitignore
  git add . >/dev/null
  git commit --allow-empty -a -m"Include lib: ${date}" >/dev/null

  git push --force production master

  # Generate source contexts for debugging.
  for service in $services; do
    gcloud debug source gen-repo-info-file \
        --output-directory=gae/$service \
        --source-directory=gae/$service;
    cat gae/$service/source-context.json
  done;

  # Deploy apps
  yes|gcloud app deploy \
    gae/frontend/cron.yaml \
    gae/frontend/index.yaml \
    $(for service in ${services}; do echo gae/${service}/app.yaml; done) \
    ;

  # Delete older versions.
  for service in ${services}; do
    if [[ "$service" == "frontend" ]]; then
      # For the sake of gae, our frontend is actually the default service.
      service="default";
    fi
    delete_old_versions $service 2;
  done;

  # Remove the generated source contexts
  rm gae/*/source-context.json >/dev/null 2>&1

  # Break apart the include lib commit.
  git reset HEAD~

  # And then check that out, effectively reverting to the working set.
  git checkout .

  # Break apart the working set commit, back to where we started before
  # the deploy script.
  git reset HEAD~

  # And restore the dev environment config.
  set_local_environment
}

main "$@"

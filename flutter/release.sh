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

# Build a production apk.

source setup/base.sh

ANDROID_BUILD_GRADLE="flutter/android/app/build.gradle"
ANDROID_APK_LOCATION="flutter/build/app/outputs/apk/release/app-release.apk"
ANDROID_RELEASE_OUTPUT_JSON="flutter/build/app/outputs/apk/release/output.json"

function main() {
  # Args
  local build_number="$(printf '%02d' $1)"

  # Verify repo
  local repo_path="$(get_repo_path)";

  set_prod_environment

  # Construct version_code.
  local date_string="$(date '+%Y%m%d')"
  local version_code="${date_string}${build_number}"

  echo ""
  echo "Releasing ${version_code}."
  echo ""

  echo ""
  echo "Temporarily modifying build.gradle."

  sed -i \
      -e "s/\(versionCode\) \(.*\)$/\1 ${version_code}/" \
      -e "s/\(versionName\) \(.*\)$/\1 \"${version_code}\"/" \
      "${ANDROID_BUILD_GRADLE}"

  echo ""
  echo "Modifying API..."
  ./gae/update_api.sh > /dev/null 2>&1

  echo ""
  echo "Building..."
  pushd flutter
  flutter build apk \
      -t lib/app.dart \
      --build-number="${version_code}" \
      --build-name="${version_code}"

  local build_code="$?"
  if [ "$build_code" -ne 0 ]; then
    echo "Unable to build!"
  fi
  popd

  echo "Restoring API..."
  ./gae/update_api.sh local > /dev/null 2>&1

  echo "Reverting build.gradle."
  git checkout "${ANDROID_BUILD_GRADLE}"

  # And restore the dev environment config.
  set_local_environment

  if [ "$build_code" -ne 0 ]; then
    echo ""
    echo "Unable to build!"
  else
    echo ""
    echo "Built ${version_code} at ${repo_path}/${ANDROID_APK_LOCATION}"
    cat "${ANDROID_RELEASE_OUTPUT_JSON}" \
        | python -m json.tool | pygmentize -l json
    python flutter/play_upload.py \
        -p cc.bikebuds \
        -a flutter/build/app/outputs/apk/release/app-release.apk \
        -s environments/prod/service_keys/play-developer-api.json \
        -t internal
  fi
}

main "$@"

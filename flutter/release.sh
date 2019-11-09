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

source tools/scripts/base.sh

ANDROID_BUILD_GRADLE="flutter/android/app/build.gradle"
ANDROID_AAB_LOCATION="flutter/build/app/outputs/bundle/release/app.aab"
ANDROID_RELEASE_OUTPUT_JSON="flutter/build/app/intermediates/merged_manifests/release/output.json"
API_SERVICE_JSON="environments/prod/service_keys/play-developer-api.json"

function ctrl_c() {
  echo "Trapped and ignored ctrl+c"
}
trap ctrl_c INT

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
  echo "Building..."
  pushd flutter
  flutter build appbundle \
      -t lib/app.dart \
      --target-platform android-arm,android-arm64 \
      --build-number="${version_code}" \
      --build-name="${version_code}"

  local build_code="$?"
  if [ "$build_code" -ne 0 ]; then
    echo "Unable to build!"
  fi
  popd

  if [ "$build_code" -ne 0 ]; then
    echo ""
    echo "Unable to build!"
  else
    echo ""
    echo "Built ${version_code} at ${repo_path}/${ANDROID_AAB_LOCATION}"
    cat "${ANDROID_RELEASE_OUTPUT_JSON}" \
        | python -m json.tool | pygmentize -l json
    python flutter/play_upload.py \
        -p cc.bikebuds \
        -a "${ANDROID_AAB_LOCATION}" \
        -s "${API_SERVICE_JSON}" \
        -t internal
  fi

  echo "Reverting build.gradle."
  git checkout "${ANDROID_BUILD_GRADLE}"

  # And restore the dev environment config.
  set_dev_environment
}

main "$@"

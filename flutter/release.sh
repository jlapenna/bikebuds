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

ANDROID_BUILD_GRADLE="android/app/build.gradle"
ANDROID_AAB_LOCATION="build/app/outputs/bundle/release/app.aab"
ANDROID_RELEASE_OUTPUT_JSON="build/app/intermediates/merged_manifests/release/output.json"
API_SERVICE_JSON="../environments/prod/service_keys/play-developer-api.json"

function ctrl_c() {
  echo "Trapped and ignored ctrl+c"
}
trap ctrl_c INT

function main() {
  # Verify repo
  local repo_path="$(get_repo_path)";

  # Flag defaults
  local android="";
  local ios="";
  local web="";
  local build_number="00"

  while getopts "awn:" OPTION
  do
    case $OPTION in
      a)
        android="android"
        ;;
      i)
        ios="ios"
        ;;
      w)
        web="web"
        ;;
      n)
        build_number="$(printf '%02d' $OPTARG)"
        echo "Build Number: $build_number"
        ;;
      \?)
        echo "Help, -a for android; -w for web, -n for a build number"
        exit
        ;;
    esac
  done

  if [[ "$android" == "" && "$ios" == "" && "$web" == "" ]]; then
    echo "No releases selected, aborting";
    exit;
  fi

  # Constuct a version code (from build number and date)
  local date_string="$(date '+%Y%m%d')"
  local version_code="${date_string}${build_number}"

  # Enable the prod environment.
  set_prod_environment
  pushd flutter

  if [[ "$android" ]]; then
    build_android "${version_code}"
  fi;
  if [[ "$web" ]]; then
    build_web "${version_code}"
  fi;

  # Restore the original environment.
  popd
  set_dev_environment
}

function build_web() {
  local version_code="$1";

  echo ""
  echo "Web"

  echo ""
  echo "Building..."
  flutter build web \
      --release \
      ;

  local build_code="$?"
  if [[ ${build_code} != 0 ]]; then
    echo ""
    echo "Unable to build!"
  else
    echo ""
    echo "Releasing..."

    pushd ../firebase/bikebuds-next
    firebase deploy \
        --only hosting \
        --message "Build: ${build_version}" \
        ;
    popd
  fi
}

function build_android() {
  local version_code="$1";

  echo ""
  echo "Android: ${version_code}."

  echo ""
  echo "Temporarily modifying build.gradle."

  sed -i \
      -e "s/\(versionCode\) \(.*\)$/\1 ${version_code}/" \
      -e "s/\(versionName\) \(.*\)$/\1 \"${version_code}\"/" \
      "${ANDROID_BUILD_GRADLE}"

  echo ""
  echo "Building..."
  flutter build appbundle \
      --target-platform android-arm,android-arm64 \
      --build-number="${version_code}" \
      --build-name="${version_code}" \
      ;

  local build_code="$?"
  if [[ ${build_code} != 0 ]]; then
    echo ""
    echo "Unable to build!"
  else
    echo ""
    echo "Built ${version_code} at ${ANDROID_AAB_LOCATION}"
    cat "${ANDROID_RELEASE_OUTPUT_JSON}" \
        | python -m json.tool | pygmentize -l json \
        ;

    echo ""
    echo "Releasing..."
    python play_upload.py \
        -p cc.bikebuds \
        -a "${ANDROID_AAB_LOCATION}" \
        -s "${API_SERVICE_JSON}" \
        -t internal \
        ;
  fi

  echo "Reverting build.gradle."
  git checkout "${ANDROID_BUILD_GRADLE}"
}

main "$@"

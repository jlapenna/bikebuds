#!/bin/bash
# Update API.

source setup/base.sh

API="bikebuds"
VERSION="v1"


function main() {
  local is_local="$1";
  if [[ "$is_local" ]]; then
    local hostname="${LOCAL_API_HOSTNAME}";
  else
    local hostname="${PROD_API_HOSTNAME}";
  fi

  local repo_path="$(get_repo_path)";

  local disc_gen_path=$(readlink -f "${repo_path}/generated/discoveryapis_generator")
  local disc_gen_resources_path="${disc_gen_path}/lib/src/dart_resources.dart"
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the discovery generator path, did you install it?"
    exit 1;
  elif [ -n "$(grep "non-required path parameter" "${disc_gen_resources_path}")" ]; then
    echo "Discovery generators still have the bad non-required clause. Fix it."
    exit 1;
  fi

  local env_path=$(readlink -f "${repo_path}/appengine_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Using virtual environment at ${env_path}"
  source "${env_path}/bin/activate"

  local api_path="${repo_path}/gae/api"
  local tmp_path=$(mktemp -d);
  local zipfile="${API}-${VERSION}.zip"
  local zip_path="${tmp_path}/${API}-${VERSION}.zip"
  local spec_path="${api_path}/${API}${VERSION}openapi.json"
  local discovery_path="${api_path}/${API}-${VERSION}.discovery"

  # These commands do accept -a but it doesn't seem to actually respect that
  # flag completely, as evidenced by failures not finding files from /lib/...
  pushd "${api_path}"

  echo "Generating openapi spec for deploy."
  python "lib/endpoints/endpointscfg.py" get_openapi_spec main.BikebudsApi \
      --hostname "${PROD_API_HOSTNAME}" \
     ;
  if [[ "$?" != 0 || ! -e "${spec_path}" ]]; then
    echo "spec file not created."
    exit 1;
  fi

  echo "Generating discovery doc for javascript and dart."
  python "lib/endpoints/endpointscfg.py" get_discovery_doc main.BikebudsApi \
      --hostname "${hostname}" \
     ;
  if [[ "$?" != 0 || ! -e "${discovery_path}" ]]; then
    echo "json discovery file not created."
    exit 1;
  fi

  echo "Generating jar zip for android."
  python "lib/endpoints/endpointscfg.py" get_client_lib java main.BikebudsApi \
      --hostname "${PROD_API_HOSTNAME}" \
      -o "${tmp_path}" \
      -bs gradle \
     ;
  if [[ "$?" != 0 || ! -e "${zip_path}" ]]; then
    echo "zip file for client not created."
    exit 1;
  fi

  popd

  echo "Building the android library."
  unzip -o "${zip_path}" -d "${tmp_path}"
  pushd "${tmp_path}/${API}"
  gradle build
  gradle install
  popd

  echo "Building the dart library."
  local tmp_dart_path="$(mktemp -d)"
  cp "$discovery_path" "$tmp_dart_path/bikebuds.discovery.json"
  dart "${disc_gen_path}/bin/generate.dart" \
      package \
      -i "${tmp_dart_path}" \
      -o generated/bikebuds_api \
      --package-name=bikebuds_api
}

main "$@"


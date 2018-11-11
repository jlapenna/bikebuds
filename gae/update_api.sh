#!/bin/bash
# Update API.

source gae/base.sh

HOSTNAME="api.bikebuds.cc"
API="bikebuds"
VERSION="v1"


function main() {
  local repo_path="$(get_repo_path)";

  local env_path=$(readlink -f "${HOME}/appengine_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  local api_path="${repo_path}/gae/api"
  local tmp_path=$(mktemp -d);
  local zipfile="${API}-${VERSION}.zip"
  local zip_path="${tmp_path}/${API}-${VERSION}.zip"
  local spec_path="${api_path}/${API}${VERSION}openapi.json"
  local discovery_path="${api_path}/${API}-${VERSION}.discovery"
  local jar_path="${tmp_path}/${API}/build/libs/${API}-${VERSION}-*-SNAPSHOT.jar"
  local jar_dest="${repo_path}/android/app/libs/bikebuds.jar"

  echo "Using virtual environment at ${env_path}"
  source "${env_path}/bin/activate"

  python "${api_path}/lib/endpoints/endpointscfg.py" get_openapi_spec main.BikebudsApi \
      -a "${api_path}" \
      --hostname "${HOSTNAME}" \
      -o "${api_path}" \
     ;
  if [[ "$?" != 0 || ! -e "${spec_path}" ]]; then
    echo "spec file not created."
    exit 1;
  fi
  python "${api_path}/lib/endpoints/endpointscfg.py" get_discovery_doc main.BikebudsApi \
      -a "${api_path}" \
      --hostname "${HOSTNAME}" \
      -o "${api_path}" \
     ;
  if [[ "$?" != 0 || ! -e "${discovery_path}" ]]; then
    echo "json discovery file not created."
    exit 1;
  fi
  python "${api_path}/lib/endpoints/endpointscfg.py" get_client_lib java main.BikebudsApi \
      -a "${api_path}" \
      --hostname "${HOSTNAME}" \
      -o "${tmp_path}" \
      -bs gradle \
     ;
  if [[ "$?" != 0 || ! -e "${zip_path}" ]]; then
    echo "zip file for client not created."
    exit 1;
  fi

  # Extract then build the library.

  unzip -o "${zip_path}" -d "${tmp_path}"

  pushd "${tmp_path}/${API}"
  gradle build
  popd
  cp -f ${jar_path} "${jar_dest}"  # unquoted src to preserve wildcard
  if [[ "$?" != 0 || ! -e "${jar_dest}" ]]; then
    echo "jar file not copied."
    exit 1;
  fi
}

main "$@"


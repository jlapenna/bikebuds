#!/bin/bash

PROD_FRONTEND_URL='https://www.bikebuds.cc'
PROD_API_HOSTNAME='api.bikebuds.cc'
PROD_API_URL="https://${PROD_API_HOSTNAME}"
PROD_BACKEND_URL='https://backend.bikebuds.cc'

LOCAL_FRONTEND_URL='http://localhost:8081'
LOCAL_API_HOSTNAME='localhost:8082'
LOCAL_API_URL="http://${LOCAL_API_HOSTNAME}"
LOCAL_BACKEND_URL='http://localhost:8083'

function verify_deps() {
  if [[ ! "$(command -v virtualenv)" ]]; then
    echo 'Error: virtualenv is not installed. Quitting.' >&2
    exit 1
  fi
  if [[ ! "$(command -v pip2)" ]]; then
    echo 'Error: pip2 is not installed. Quitting.' >&2
    exit 1
  fi
  if [[ ! "$(command -v npm)" ]]; then
    echo 'Error: npm is not installed. Quitting.' >&2
    exit 1
  fi
}

function get_repo_path() {
  verify_deps

  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename ${repo_path})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo. Quitting." >&2
    exit 1;
  fi
  echo "${repo_path}";
}

function get_env_path() {
  local env_path=$(readlink -f "$(get_repo_path)/appengine_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment. Quitting." >&2
    exit 1;
  fi
  echo "${env_path}";
}

function activate_env() {
  local env_path="$(get_env_path)";
  echo "Activating virtual environment at ${env_path}"
  virtualenv --python python2 "${env_path}" >/dev/null 2>&1
  source "${env_path}/bin/activate"
  if [ "$?" -ne 0 ]; then
    echo "Unable to setup virtual environment. Quitting." >&2
    exit 2;
  fi
}

get_repo_path

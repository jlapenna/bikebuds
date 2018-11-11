#!/bin/bash

PROD_FRONTEND_URL='https://www.bikebuds.cc'
PROD_API_HOSTNAME='api.bikebuds.cc'
PROD_API_URL="https://${PROD_API_HOSTNAME}"
PROD_BACKEND_URL='https://backend.bikebuds.cc'

LOCAL_FRONTEND_URL='http://localhost:8080'
LOCAL_API_HOSTNAME='localhost:8081'
LOCAL_API_URL="http://${LOCAL_API_HOSTNAME}"
LOCAL_BACKEND_URL='http://localhost:8082'


function get_repo_path() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename ${repo_path})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo."
    exit 1;
  fi
  echo "${repo_path}";
}

get_repo_path

#!/bin/bash
# Do development in the backend gae environment.

function main() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename ${repo_path})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo."
    exit 1;
  fi

  local env_path=$(readlink -f "$HOME/standalone_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Using virtual environment at ${env_path}"
  source "${env_path}/bin/activate"

  sed -i "s/var backendHostUrl = .*/var backendHostUrl = 'http:\/\/localhost:8081';/" gae/frontend/main.js

  cd gae/backend;

  ipython
}

main "$@"


#!/bin/bash
# Run a local instance, rewriting code for local development.

function main() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename ${repo_path})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo."
    exit 1;
  fi

  local env_path=$(readlink -f "$HOME/appengine_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Using virtual environment at ${env_path}"
  virtualenv --python python2 "${env_path}"
  source "${env_path}/bin/activate"

  sed -i "s/var backendHostUrl = .*/var backendHostUrl = 'http:\/\/localhost:8081';/" gae/frontend/main.js
  dev_appserver.py gae/frontend/app.yaml gae/backend/app.yaml
}

main "$@"

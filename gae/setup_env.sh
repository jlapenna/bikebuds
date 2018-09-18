#!/bin/bash
# Configures an environment to run the backend in.
#
# ./gae/setup_env.sh

function main() {
  local repo_basepath=$(readlink -e "$PWD")
  if [[ "$(readlink $PWD)" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo."
    exit 1;
  fi

  local backend_basepath="${repo_basepath}/backend"
  local env_basepath=$(readlink -f "$HOME/appengine_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Setting up virtual environment at ${env_basepath}"
  virtualenv --python python2 "${env_basepath}"
  source "${env_basepath}/bin/activate"

  echo "Installing backend dependencies."
  pip install -t lib -r "${backend_basepath}/requirements.txt"
}

main "$@"

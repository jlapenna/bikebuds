#!/bin/bash
# Configures an environment to mess around with, one that looks similar to the
# gae standard environment.
#
# ./gae/setup_standalone.sh

function main() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename $repo_path)" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo."
    exit 1;
  fi
  local backend_path="${repo_path}/gae/backend"

  local env_path=$(readlink -f "$HOME/standalone_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Setting up environment for standalone dev..."
  echo ""
  echo "Setting up virtual environment at ${env_path}"
  virtualenv --python python2 "${env_path}"
  source "${env_path}/bin/activate"

  echo ""
  echo "Installing backend dependencies."
  pip install -r "${backend_path}/requirements.txt"

  echo ""
  echo "Installing other useful things."
  pip install ipython
}

main "$@"

#!/bin/bash
# Configures an environment to run the backend in.
#
# ./gae/setup_env.sh

function main() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename $repo_path)" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo."
    exit 1;
  fi
  local backend_path="${repo_path}/gae/backend"

  local env_path=$(readlink -f "$HOME/appengine_env")
  if [ "$?" -ne 0 ]; then
    echo "Unable to locate the virtual environment"
    exit 1;
  fi

  echo "Setting up environment for deployment..."
  echo ""
  echo "Setting up virtual environment at ${env_path}"
  virtualenv --python python2 "${env_path}"
  source "${env_path}/bin/activate"

  echo ""
  echo "Installing backend dependencies."
  pip install -t "${backend_path}/lib" -r "${backend_path}/requirements.txt"

  echo ""
  echo "Copying over service keys."
  cp -rf "${repo_path}/private/service_keys" "${backend_path}/lib/"
}

main "$@"

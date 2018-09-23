#!/bin/bash
# Deploy the service to appengine, rewriting code to support production.

function main() {
  local repo_path=$(readlink -e "$PWD")
  if [[ "$(basename ${repo_path})" != "bikebuds" ]]; then
    echo "Must be in the bikebuds code repo."
    exit 1;
  fi

  sed -i "s/var backendHostUrl = .*/var backendHostUrl = 'https:\/\/backend-dot-bikebuds-app.appspot.com';/" gae/frontend/main.js
  gcloud --project=bikebuds-app app deploy gae/backend/index.yaml gae/frontend/app.yaml backend/app.yaml
}

main "$@"

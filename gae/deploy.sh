#!/bin/bash
# Deploy the service to appengine, rewriting code to support production.

function main() {
  sed -i "s/var backendHostUrl = .*/var backendHostUrl = 'https:\/\/backend-dot-bikebuds-app.appspot.com';/" frontend/main.js
  gcloud --project=bikebuds-app app deploy backend/index.yaml frontend/app.yaml backend/app.yaml
}

main "$@"

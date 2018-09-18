#!/bin/bash
# Run a local instance, rewriting code for local development.

function main() {
  sed -i "s/var backendHostUrl = .*/var backendHostUrl = 'localhost:8081';/" frontend/main.js
  dev_appserver.py frontend/app.yaml backend/app.yaml
}

main "$@"

#!/bin/bash
# Update API.

source tools/scripts/base.sh

API="bikebuds"
VERSION="v1"

REPO_PATH="$(get_repo_path)";
GENERATOR_PATH="${REPO_PATH}/generated/openapi-generator";

function main() {
  generate dart "${REPO_PATH}/generated/bikebuds_api";
  generate python "${REPO_PATH}/generated/python_bikebuds_api";
}

function generate() {
  local lang="$1"
  local target_path="$2"
  echo "Generating discovery doc for javascript and dart."
  pushd $GENERATOR_PATH;
  rm -rf $target_path
  java -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar \
      generate \
      -i http://localhost:8082/swagger.json \
      -g "${lang}" \
      --additional-properties=pubName=bikebuds_api \
      --additional-properties=packageName=bikebuds_api \
      --additional-properties=projectName=bikebuds-api \
      -o $target_path \
      -DbrowserClient=false \
      ;
  popd
}

main "$@"


#!/bin/bash
# Update API.

source tools/scripts/base.sh || exit 1

API="bikebuds"
VERSION="v1"

GENERATOR_PATH="${BIKEBUDS_PATH}/generated/openapi-generator";

function main() {
  generate dart "${BIKEBUDS_PATH}/generated/bikebuds_api";
  generate python "${BIKEBUDS_PATH}/generated/python_bikebuds_api";
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


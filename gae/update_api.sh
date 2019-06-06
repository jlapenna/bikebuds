#!/bin/bash
# Update API.

source tools/scripts/base.sh

API="bikebuds"
VERSION="v1"


function main() {
  local repo_path="$(get_repo_path)";

  local openapi_generator_path="${repo_path}/generated/openapi-generator";
  local target_path="${repo_path}/generated/bikebuds_api";

  echo "Generating discovery doc for javascript and dart."
  pushd $openapi_generator_path;
  rm -rf $target_path
  java -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar \
      generate \
      -i http://localhost:8082/swagger.json \
      -g dart \
      --additional-properties=pubName=bikebuds_api \
      -o $target_path \
      -DbrowserClient=false \
      ;
}

main "$@"


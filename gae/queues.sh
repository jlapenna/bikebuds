#!/bin/bash

source tools/scripts/base.sh
load_config

QUEUES="default events notifications slack"

function main() {
  for queue in ${QUEUES}; do 
    gcloud --project=bikebuds-app tasks queues update ${queue} \
        --max-dispatches-per-second=1 \
        --max-attempts=2 \
        --min-backoff=60s \
        ;

  done
  gcloud --project=bikebuds-app tasks queues update "backfill" \
      --max-dispatches-per-second=1 \
      --max-attempts=1 \
      --min-backoff=60s \
      ;
}

main "$@"

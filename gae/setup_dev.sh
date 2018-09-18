#!/bin/bash
# Dependencies for development, in order to start a dev server, for example.

function main() {
  sudo apt install python python-dev python3 python3-dev python-pip virtualenv
}

main "$@"

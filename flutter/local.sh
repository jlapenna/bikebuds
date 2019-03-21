#!/bin/bash
# Configures a device for development with a local backend.

function main() {
  local serial_device="${1}";
  if [[ "${serial_device}" != "" ]]; then
    serial_device="-s ${serial_device}"
  fi

  echo "Setting up reverse port forwards."
  adb ${serial_device} reverse tcp:8080 tcp:8080
  adb ${serial_device} reverse tcp:8081 tcp:8081
  adb ${serial_device} reverse tcp:8082 tcp:8082

  echo "Increasing logging."
  adb ${serial_device} shell setprop log.tag.HttpTransport DEBUG
}

main "$@"

#!/bin/bash
#
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Dependencies for development, in order to start a dev server, for example.

source tools/scripts/base.sh

export REPO_PATH="$(get_repo_path)";

function source_files() {
  find . \
    \( \
    -path './environments/virtual' -o \
    -path './flutter/build' -o \
    -path './gae/api/lib' -o \
    -path './gae/backend/lib' -o \
    -path './gae/client/lib' -o \
    -path './gae/frontend/build' -o \
    -path './gae/frontend/lib' -o \
    -path './gae/frontend/node_modules' \
    \) -prune -o \
    \( \
        -name '*.sh' -o \
        -name '*.dart'  -o \
        -name '*.java'  -o \
        -name '*.js' -o \
        -name '*.jsx' -o \
        -name '*.py' -o \
        -name '*.json' \
    \) -type f -print \
    ;

}

function sgrep() {
  egrep "$@" $(source_files)
}
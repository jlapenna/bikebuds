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

source tools/scripts/base.sh || exit 1

function main {
  curl -H "Content-Type: application/x-www-form-urlencoded" \
      -X POST "http://localhost:8081/services/withings/events?sub_secret=XYZXYZ&service_key=ahFkZXZ-YmlrZWJ1ZHMtdGVzdHIxCxIEVXNlciISamxhcGVubmFAZ21haWwuY29tDAsSB1NlcnZpY2UiCHdpdGhpbmdzDA" \
      -d "userid=17012450&startdate=1532017199&enddate=1532017200&appli=1"
}
main

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

source tools/scripts/base.sh

load_config

function main {
  curl -H "Content-Type: application/json" \
      -X POST "http://localhost:8081/services/strava/events" \
      -d "{
           "aspect_type": "create",
           "event_time": 1549151211,
           "object_id": 2156802368,
           "object_type": "activity",
           "owner_id": 35056021,
           "subscription_id": 133263,
           "updates": {}
           }";
}
main

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

from shared import monkeypatch

import datetime
import logging
import sys

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from shared.datastore.admin import SubscriptionEvent, SyncState
from shared.datastore.services import Service


@ndb.transactional
def sync_service(service):
    sync_services([service])


@ndb.transactional(xg=True)
def sync_services(services):
    state = SyncState(completed_tasks=0)
    state_key = state.put()

    tasks = []
    for service in services:
        user_key = service.key.parent()
        service.sync_date=datetime.datetime.now()
        service.syncing = True

        tasks.append(
                taskqueue.Task(
                    url='/tasks/service_sync/' + service.key.id(),
                    target='backend',
                    params={
                        'state': state_key.urlsafe(),
                        'service': service.key.urlsafe()
                        }
                    )
                )
    state.total_tasks = len(tasks)
    state.put()

    for task in tasks:
        task.add()


@ndb.transactional
def process_event(event_entity):
    event_entity.put()
    taskqueue.add(
            countdown=60,
            url='/tasks/process_events',
            target='backend',
            _transactional=True
            )

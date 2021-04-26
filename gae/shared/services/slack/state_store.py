# Copyright 2021 Google LLC
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

import logging
import time
from logging import Logger
from uuid import uuid4

from google.cloud.datastore import Client
from google.cloud.datastore.entity import Entity
from slack_sdk.oauth.state_store.async_state_store import AsyncOAuthStateStore
from slack_sdk.oauth.state_store import OAuthStateStore


class DatastoreOAuthStateStore(OAuthStateStore, AsyncOAuthStateStore):
    def __init__(
        self,
        client: Client,
        expiration_seconds: int,
        logger: Logger = logging.getLogger(__name__),
    ):
        self.client = client
        self.expiration_seconds = expiration_seconds
        self._logger = logger

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    async def async_issue(self, *args, **kwargs) -> str:
        return self.issue(*args, **kwargs)

    async def async_consume(self, state: str) -> bool:
        return self.consume(state)

    def issue(self, *args, **kwargs) -> str:
        state = str(uuid4())
        entity = Entity(self.client.key('SlackStateStore', state))
        entity['body'] = str(time.time())
        response = self.client.put(entity)
        self.logger.debug(f"DS put response: {response}")
        return state

    def consume(self, state: str) -> bool:
        try:
            entity = self.client.get(self.client.key('SlackStateStore', state))
            if not entity:
                self.logger.debug(
                    f"Failed to find any persistent data for state: {state}"
                )
                return False
            body = entity["body"]
            created = float(body)
            expiration = created + self.expiration_seconds
            still_valid: bool = time.time() < expiration

            deletion_response = self.client.delete(entity.key)
            self.logger.debug(f"DS delete response: {deletion_response}")
            return still_valid
        except Exception as e:  # skipcq: PYL-W0703
            message = f"Failed to find any persistent data for state: {state} - {e}"
            self.logger.exception(message)
            return False

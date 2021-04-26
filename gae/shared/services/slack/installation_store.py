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

from typing import Optional
import logging

from google.cloud.datastore import Client
from google.cloud.datastore import Key
from google.cloud.datastore.entity import Entity
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.oauth.installation_store.installation_store import InstallationStore
from slack_sdk.oauth.installation_store.models.bot import Bot
from slack_sdk.oauth.installation_store.models.installation import Installation

from shared import ds_util
from shared.datastore.slack import SlackBot, SlackInstaller, SlackWorkspace


class DatastoreInstallationStore(InstallationStore, AsyncInstallationStore):
    def __init__(
        self,
        client: Client,
        parent: Optional[Key] = None,
        historical_data_enabled: bool = True,
        logger: logging.Logger = logging.getLogger(__name__),
    ):
        self.client = client
        self.parent = parent
        self.historical_data_enabled = historical_data_enabled
        self._logger = logger

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    async def async_save(self, installation: Installation):
        return self.save(installation)

    def save(self, installation: Installation):
        workspace_key = SlackWorkspace.key(
            installation.enterprise_id, installation.team_id, parent=self.parent
        )
        ds_util.client.put(Entity(workspace_key))

        entity = Entity(SlackBot.key('bot-latest', parent=workspace_key))
        entity.update(installation.to_bot().__dict__)
        response = self.client.put(entity)
        self.logger.debug(f"DS put response: {response}")

        # per workspace
        entity = Entity(SlackInstaller.key('installer-latest', parent=workspace_key))
        entity.update(installation.__dict__)
        response = self.client.put(entity)
        self.logger.debug(f"DS put response: {response}")

        # per workspace per user
        u_id = installation.user_id or "NONE"
        entity = Entity(
            SlackInstaller.key(f'installer-{u_id}-latest', parent=workspace_key)
        )
        entity.update(installation.__dict__)
        response = self.client.put(entity)
        self.logger.debug(f"DS put response: {response}")

    async def async_find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        return self.find_bot(
            enterprise_id=enterprise_id,
            team_id=team_id,
            is_enterprise_install=is_enterprise_install,
        )

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        if is_enterprise_install:
            team_id = None
        workspace_key = SlackWorkspace.key(enterprise_id, team_id, parent=self.parent)
        bot_key = SlackBot.key('bot-latest', parent=workspace_key)
        try:
            entity = self.client.get(bot_key)
            self.logger.debug(f"DS get response: {entity}")
            return Bot(**entity)
        except Exception:
            self.logger.exception(f"Failed to find bot installation for: {bot_key}")
            return None

    async def async_find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        return self.find_installation(
            enterprise_id=enterprise_id,
            team_id=team_id,
            user_id=user_id,
            is_enterprise_install=is_enterprise_install,
        )

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        if is_enterprise_install:
            team_id = None
        workspace_key = SlackWorkspace.key(enterprise_id, team_id, parent=self.parent)
        try:
            name = f"installer-{user_id}-latest" if user_id else "installer-latest"
            entity = self.client.get(SlackInstaller.key(name, parent=workspace_key))
            self.logger.debug(f"DS get response: {entity}")
            return Installation(**entity)
        except Exception as e:  # skipcq: PYL-W0703
            self.logger.exception(
                f"Failed to find an installation data for enterprise: {enterprise_id}, team: {team_id}: {e}"
            )
            return None

    async def async_delete_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str]
    ) -> None:
        return self.delete_bot(
            enterprise_id=enterprise_id,
            team_id=team_id,
        )

    def delete_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str]
    ) -> None:
        workspace_key = SlackWorkspace.key(enterprise_id, team_id, parent=self.parent)
        query = self.client.query('SlackBot', ancestor=workspace_key)
        query.keys_only()
        try:
            batch = self.client.batch()
            with batch:
                for entity in query:
                    self.logger.info(f"Queueing delete for {entity.key}")
                    batch.delete(entity.key)
        except Exception as e:  # skipcq: PYL-W0703
            self.logger.warning(
                f"Failed to find bot data for enterprise: {enterprise_id}, team: {team_id}: {e}"
            )

    async def async_delete_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
    ) -> None:
        return self.delete_installation(
            enterprise_id=enterprise_id,
            team_id=team_id,
            user_id=user_id,
        )

    def delete_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
    ) -> None:
        workspace_key = SlackWorkspace.key(enterprise_id, team_id, parent=self.parent)
        query = self.client.query('SlackInstaller', ancestor=workspace_key)
        query.keys_only()
        try:
            batch = self.client.batch()
            with batch:
                for entity in query:
                    if entity.key.name.startswith(f"installer-{user_id or ''}"):
                        self.logger.info(f"Queueing delete for {entity.key}")
                        batch.delete(entity.key)
        except Exception as e:  # skipcq: PYL-W0703
            self.logger.warning(
                f"Failed to find installation data for enterprise: {enterprise_id}, team: {team_id}: {e}"
            )

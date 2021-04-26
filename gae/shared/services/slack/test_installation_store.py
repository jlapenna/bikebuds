# Copyright 2021 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest import mock

from google.cloud.datastore.entity import Entity
from slack_sdk.oauth.installation_store.models.bot import Bot
from slack_sdk.oauth.installation_store.models.installation import Installation

from shared import ds_util
from shared.services.slack.installation_store import DatastoreInstallationStore


class DatastoreInstallationStoreTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @mock.patch('shared.ds_util.client.put')
    def test_save_enterprise_team_user(self, mock_client_put):
        workspace_key = ds_util.client.key('SlackWorkspace', 'enterprise_id-team_id')
        store = DatastoreInstallationStore(ds_util.client)
        installation = Installation(
            app_id='app_id',
            enterprise_id='enterprise_id',
            team_id='team_id',
            user_id='user_id',
        )

        store.save(installation)

        workspace_entity = mock_client_put.call_args_list[0][0][0]
        self.assertEqual(workspace_entity.key, workspace_key)

        bot_latest_entity = mock_client_put.call_args_list[1][0][0]
        self.assertEqual(bot_latest_entity.key.parent, workspace_key)
        self.assertEqual(
            bot_latest_entity.key,
            ds_util.client.key('SlackBot', 'bot-latest', parent=workspace_key),
        )

        installer_latest_entity = mock_client_put.call_args_list[2][0][0]
        self.assertEqual(
            installer_latest_entity.key,
            ds_util.client.key(
                'SlackInstaller', 'installer-latest', parent=workspace_key
            ),
        )

        installer_user_latest_entity = mock_client_put.call_args_list[3][0][0]
        self.assertEqual(
            installer_user_latest_entity.key,
            ds_util.client.key(
                'SlackInstaller', 'installer-user_id-latest', parent=workspace_key
            ),
        )

    @mock.patch('shared.ds_util.client.put')
    def test_save_enterprise_user(self, mock_client_put):
        workspace_key = ds_util.client.key('SlackWorkspace', 'enterprise_id-NONE')
        store = DatastoreInstallationStore(ds_util.client)
        installation = Installation(
            app_id='app_id', enterprise_id='enterprise_id', user_id='user_id'
        )

        store.save(installation)

        workspace_entity = mock_client_put.call_args_list[0][0][0]
        self.assertEqual(workspace_entity.key, workspace_key)

        bot_latest_entity = mock_client_put.call_args_list[1][0][0]
        self.assertEqual(bot_latest_entity.key.parent, workspace_key)
        self.assertEqual(
            bot_latest_entity.key,
            ds_util.client.key('SlackBot', 'bot-latest', parent=workspace_key),
        )

        installer_latest_entity = mock_client_put.call_args_list[2][0][0]
        self.assertEqual(
            installer_latest_entity.key,
            ds_util.client.key(
                'SlackInstaller', 'installer-latest', parent=workspace_key
            ),
        )

        installer_user_latest_entity = mock_client_put.call_args_list[3][0][0]
        self.assertEqual(
            installer_user_latest_entity.key,
            ds_util.client.key(
                'SlackInstaller', 'installer-user_id-latest', parent=workspace_key
            ),
        )

    @mock.patch('shared.ds_util.client.put')
    def test_save_user(self, mock_client_put):
        workspace_key = ds_util.client.key('SlackWorkspace', 'NONE-NONE')
        store = DatastoreInstallationStore(ds_util.client)
        installation = Installation(app_id='app_id', user_id='user_id')

        store.save(installation)

        workspace_entity = mock_client_put.call_args_list[0][0][0]
        self.assertEqual(workspace_entity.key, workspace_key)

        bot_latest_entity = mock_client_put.call_args_list[1][0][0]
        self.assertEqual(bot_latest_entity.key.parent, workspace_key)
        self.assertEqual(
            bot_latest_entity.key,
            ds_util.client.key('SlackBot', 'bot-latest', parent=workspace_key),
        )

        installer_latest_entity = mock_client_put.call_args_list[2][0][0]
        self.assertEqual(
            installer_latest_entity.key,
            ds_util.client.key(
                'SlackInstaller', 'installer-latest', parent=workspace_key
            ),
        )

        installer_user_latest_entity = mock_client_put.call_args_list[3][0][0]
        self.assertEqual(
            installer_user_latest_entity.key,
            ds_util.client.key(
                'SlackInstaller', 'installer-user_id-latest', parent=workspace_key
            ),
        )

    @mock.patch('shared.ds_util.client.get')
    def test_find_bot(self, mock_client_get):
        workspace_key = ds_util.client.key('SlackWorkspace', 'enterprise_id-team_id')
        store = DatastoreInstallationStore(ds_util.client)

        bot_entity = Entity(
            ds_util.client.key('SlackBot', 'bot-latest', parent=workspace_key)
        )
        bot_entity.update(
            Bot(
                app_id='app_id',
                bot_id='bot_id',
                bot_token='bot_token',
                bot_user_id='bot_user_id',
                installed_at=55.00,
            ).__dict__
        )
        mock_client_get.return_value = bot_entity
        found_bot = store.find_bot(enterprise_id='enterprise_id', team_id='team_id')
        self.assertIsNotNone(found_bot)
        self.assertIsInstance(found_bot, Bot)

        # Make sure we searched for the right key.
        key = mock_client_get.call_args[0][0]
        self.assertEqual(
            key, ds_util.client.key('SlackBot', 'bot-latest', parent=workspace_key)
        )

    @mock.patch('shared.ds_util.client.get')
    def test_find_installation(self, mock_client_get):
        workspace_key = ds_util.client.key('SlackWorkspace', 'enterprise_id-team_id')
        store = DatastoreInstallationStore(ds_util.client)
        installation_entity = Entity(
            ds_util.client.key(
                'SlackInstaller', 'installer-latest', parent=workspace_key
            )
        )
        installation_entity.update(
            Installation(
                app_id='app_id',
                enterprise_id='enterprise_id',
                team_id='team_id',
                user_id='user_id',
            ).__dict__
        )
        mock_client_get.return_value = installation_entity
        found_installation = store.find_installation(
            enterprise_id='enterprise_id', team_id='team_id'
        )
        self.assertIsNotNone(found_installation)
        self.assertIsInstance(found_installation, Installation)

        # Make sure we searched for the right key.
        key = mock_client_get.call_args[0][0]
        self.assertEqual(
            key,
            ds_util.client.key(
                'SlackInstaller', 'installer-latest', parent=workspace_key
            ),
        )

    def test_installation_to_entity_to_installation(self):
        installation = Installation(app_id='app_id', user_id='user_id')
        entity = Entity()
        entity.update(installation.__dict__)
        from_entity = Installation(**entity)
        self.assertEqual(installation.__dict__, from_entity.__dict__)

    def test_installation_bot_to_entity_to_bot(self):
        installation = Installation(app_id='app_id', user_id='user_id')

        bot = installation.to_bot()
        entity = Entity()
        entity.update(bot.__dict__)
        from_entity = Bot(**entity)
        self.assertEqual(bot.__dict__, from_entity.__dict__)

    def test_bot_to_entity_to_bot(self):
        bot = Bot(
            app_id='app_id',
            bot_id='bot_id',
            bot_token='bot_token',
            bot_user_id='bot_user_id',
            installed_at=55.00,
        )
        entity = Entity()
        entity.update(bot.__dict__)
        from_entity = Bot(**entity)
        self.assertEqual(bot.__dict__, from_entity.__dict__)

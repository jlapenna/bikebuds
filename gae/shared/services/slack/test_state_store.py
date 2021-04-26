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

from shared import ds_util
from shared.services.slack.state_store import DatastoreOAuthStateStore


class DatastoreOAuthStateStoreTest(unittest.TestCase):
    @mock.patch('uuid.uuid4', mock.MagicMock(return_value='somestatefromuuid'))
    @mock.patch('time.time', mock.MagicMock(return_value=1000.000))
    @mock.patch('shared.ds_util.client.put')
    def test_issue(self, mock_client_put):
        store = DatastoreOAuthStateStore(ds_util.client, 100)
        state_name = store.issue()

        mock_client_put.assert_called_once()
        entity = mock_client_put.call_args[0][0]
        self.assertEqual(entity.key.name, state_name)
        self.assertEqual(entity['body'], '1000.0')

    @mock.patch('time.time', mock.MagicMock(return_value=1000.000))
    @mock.patch('shared.ds_util.client.delete')
    @mock.patch('shared.ds_util.client.get')
    def test_consume_valid(self, mock_client_get, mock_client_delete):
        entity = Entity(ds_util.client.key('SlackStateStore', 'somestatefromuuid'))
        entity['body'] = '1000.0'
        mock_client_get.return_value = entity

        store = DatastoreOAuthStateStore(ds_util.client, 100)
        result = store.consume('somestatefromuuid')
        self.assertTrue(result)

        mock_client_get.assert_called_once()
        ds_util.client.delete.assert_called_once()
        key = mock_client_delete.call_args[0][0]
        self.assertEqual(key.name, 'somestatefromuuid')

    @mock.patch('time.time', mock.MagicMock(return_value=2000.000))
    @mock.patch('shared.ds_util.client.delete')
    @mock.patch('shared.ds_util.client.get')
    def test_consume_expired(self, mock_client_get, mock_client_delete):
        entity = Entity(ds_util.client.key('SlackStateStore', 'somestatefromuuid'))
        entity['body'] = '1000.0'
        mock_client_get.return_value = entity

        store = DatastoreOAuthStateStore(ds_util.client, 100)
        result = store.consume('somestatefromuuid')
        self.assertFalse(result)

        mock_client_get.assert_called_once()
        ds_util.client.delete.assert_called_once()
        key = mock_client_delete.call_args[0][0]
        self.assertEqual(key.name, 'somestatefromuuid')

    @mock.patch('time.time', mock.MagicMock(return_value=2000.000))
    @mock.patch('shared.ds_util.client.delete', mock.MagicMock())
    @mock.patch('shared.ds_util.client.get')
    def test_consume_unknown(self, mock_client_get):
        store = DatastoreOAuthStateStore(ds_util.client, 100)
        result = store.consume('somestatefromuuid')
        self.assertFalse(result)

        mock_client_get.assert_called_once()

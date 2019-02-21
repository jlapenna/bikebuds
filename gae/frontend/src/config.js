/**
 * Copyright 2018 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import config_json from './config.json';

export const config = {
  projectId: config_json['project_id'],
  apiKey: config_json['api_key'],
  authDomain: config_json['auth_domain'],
  databaseURL: config_json['database_url'],
  mapsApiKey: config_json['maps_api_key'],
  storageBucket: config_json['storage_bucket'],
  messagingSenderId: config_json['message_sender_id'],
  vapidKey: config_json['vapid_key'],
  devserverUrl: config_json['devserver_url'],
  frontendUrl: config_json['frontend_url'],
  apiUrl: config_json['api_url'],
  backendUrl: config_json['backend_url']
};

export const nextConfig = {
  projectId: config_json['next_project_id'],
  apiKey: config_json['next_api_key'],
  authDomain: config_json['next_auth_domain'],
  databaseURL: config_json['next_database_url'],
  storageBucket: config_json['next_storage_bucket'],
  messagingSenderId: config_json['next_message_sender_id']
};

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

import logging

from google.cloud.datastore.entity import Entity

from firebase_admin import messaging

from shared import ds_util


def active_clients(user_key):
    query = ds_util.client.query(kind='ClientState', ancestor=user_key)
    query.add_filter('active', '!=', False)
    return [c for c in query.fetch()]


def send(user_key, clients, notif_fn, *args, **kwargs):
    """Sends a notification.

    Args:
        user: User - The entity being sent the notification.
        clients: [ClientState] - Clients to send the notification.
        notif_fn: function - *args and **kwargs are passed to this function,
            a ClientMessage will be passed as a 'client' kwarg.
    """
    with ds_util.client.transaction():
        fcm_message = Entity(ds_util.cient.key('FcmMessage', parent=user_key))
        logging.debug('Sending notification to %s clients', len(clients))
        for client_state in clients:
            message = notif_fn(*args, client=client_state.client, **kwargs)
            try:
                response = messaging.send(message)
                logging.debug('fcm_util.send: Success: %s, %s, %s', user_key, message,
                        response)
                fcm_message.add_delivery(client_state, message, response)
            except messaging.ApiCallError as e:
                logging.error('fcm_util.send: Failure: %s, %s', user_key, e)
                fcm_message.add_failure(client_state, message, e)
        ds_util.client.put(fcm_message)

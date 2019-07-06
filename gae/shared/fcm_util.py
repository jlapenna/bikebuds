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

import datetime
import logging

from firebase_admin import messaging

from shared import ds_util
from shared.datastore.fcm import FcmMessage, FcmSendEvent


def active_clients(user_key):
    query = ds_util.client.query(kind='ClientState', ancestor=user_key)
    query.add_filter('active', '=', True)
    return [c for c in query.fetch()]


def best_clients(user_key):
    query = ds_util.client.query(
        kind='ClientState', ancestor=user_key, order=['-modified']
    )
    query.add_filter('active', '=', True)
    return [c for c in query.fetch(1)]


def send(user_key, clients, notif_fn, *args, **kwargs):
    """Sends a notification.

    Args:
        user: User - The entity being sent the notification.
        clients: [ClientState] - Clients to send the notification.
        notif_fn: function - *args and **kwargs are passed to this function,
            a ClientMessage will be passed as a 'client' kwarg.
    """
    with ds_util.client.transaction():
        fcm_send_event = FcmSendEvent.to_entity(
            {'date': datetime.datetime.utcnow(), 'messages': []}, parent=user_key
        )
        logging.debug('Sending notification to %s clients', len(clients))
        for client_state in clients:
            message = notif_fn(*args, client=client_state, **kwargs)
            try:
                response = messaging.send(message)
                logging.debug(
                    'fcm_util.send: Success: %s, %s, %s', user_key, message, response
                )
                _add_delivery(fcm_send_event, client_state, message, response)
            except Exception as e:
                logging.exception('fcm_util.send: Failure: %s', user_key)
                _add_delivery(fcm_send_event, client_state, message, e)
        ds_util.client.put(fcm_send_event)


def _add_delivery(fcm_send_event, client_store, message, response):
    success = not isinstance(response, Exception)
    if message.data is not None:
        e = FcmMessage.to_entity(
            {
                'response': str(response),
                'client_store': client_store.key,
                'success': success,
            }
        )
        fcm_send_event['messages'].append(e)
    elif message.notification is not None:
        e = FcmMessage.to_entity(
            {
                'response': str(response),
                'client_store': client_store.key,
                'success': success,
                'title': message.notification.title,
                'body': message.notification.body,
            }
        )
        fcm_send_event['messages'].append(e)
    else:
        logging.error('Cannot add delivery of unknown message type')

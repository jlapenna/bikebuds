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

from google.appengine.ext import ndb

from firebase_admin import messaging

from shared.datastore.admin import FcmMessage

@ndb.transactional
def send(user, clients, notif_fn, *args, **kwargs):
    """Sends a notification.

    Args:
        user: User - The entity being sent the notification.
        clients: [ClientStore] - Clients to send the notification.
        notif_fn: function - *args and **kwargs are passed to this function,
            a client_store will be passed as an additional kwarg.
    """
    notification = FcmMessage(parent=user.key)
    for client_store in clients:
        message = notif_fn(*args, client_store=client_store, **kwargs) 
        try:
            response = messaging.send(message)
            logging.debug('WeightTrendWorker: %s daily_weight_notif: sent: %s -> %s',
                    user.key, message, response)
            notification.add_delivery(client_store, message, response)
        except messaging.ApiCallError, e:
            logging.error('WeightTrendWorker: %s daily_weight_notif: failed: %s',
                    user.key, e)
            notification.add_failure(client_store, message, e)
    notification.put()

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

import { config } from './config';

export function createSession(firebase, responseCallback) {
  if (config.is_dev && config.fake_user) {
    responseCallback({ status: 200 });
    return;
  }
  firebase.auth.currentUser.getIdTokenResult().then(idTokenResult => {
    fetch(config.frontend_url + '/services/session', {
      /* Set header for the XMLHttpRequest to get data from the web server
       * associated with userIdToken */
      headers: {
        Authorization: 'Bearer ' + idTokenResult.token,
      },
      method: 'POST',
      credentials: 'include',
    }).then(responseCallback);
  });
}

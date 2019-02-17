/**
 * Copyright 2019 Google Inc. All Rights Reserved.
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

import React, { Component } from 'react';

export default class Consent extends Component {
  render() {
    return (
      <div>
        <p>
          Welcome to bikebuds! Here is a summary of our terms and privacy
          policy.
        </p>
        <div>
          We will:
          <ul>
            <li>
              <strong>Use</strong> your data (such as fitness stats or location)
              to provide services for you and other users.
            </li>
            <li>
              <strong>Collect</strong> your data from several third-party
              services.
            </li>
            <li>
              <strong>Copy</strong> your data and use it on our site to provide
              services.
            </li>
            <li>
              <strong>Share</strong> your data with other users of bikebuds and
              its administrators. In some cases, not applying the privacy
              controls of source services, in order to provide a better
              experience.
            </li>
          </ul>
          <p />
          You will:
          <ul>
            <li>
              <strong>Not hold us responsible</strong> for damages or
              consequences arising from use of the service.
            </li>
            <li>Not use the site in a deceptive or criminal manner.</li>
          </ul>
          <p />
          <em>This is not an officially supported Google product.</em>
          <p />
        </div>
      </div>
    );
  }
}

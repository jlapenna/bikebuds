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

import React from 'react';
import ReactDOM from 'react-dom';

import Preferences from './Preferences';
import { ProfileState } from './ProfileWrapper';

it('renders without crashing', () => {
  const firebaseUser = {
    displayName: 'Display Name',
    photoUrl: '/logo-round.svg',
  };
  const bikebudsApi = {
    get_clients: () => Promise.resolve({ body: [] }),
  };

  // this.props.profile.user.properties.preferences.units
  const profile = new ProfileState();
  profile.user = { properties: { preferences: { units: 'IMPERIAL' } } };
  profile.athlete = { properties: {} };

  const div = document.createElement('div');
  ReactDOM.render(
    <Preferences
      bikebudsApi={bikebudsApi}
      firebaseUser={firebaseUser}
      profile={profile}
    />,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

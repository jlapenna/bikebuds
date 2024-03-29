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

import { BrowserRouter as Router } from 'react-router-dom';

import ProfileCard from './ProfileCard';

it('renders without crashing', () => {
  const firebase = createFirebaseState();
  const firebaseUser = {
    displayName: 'Display Name',
    photoUrl: '/logo-round.svg',
  };
  const profile = {
    athlete: { properties: { city: 'San Francisco' } },
  };
  const match = {};
  const div = document.createElement('div');
  ReactDOM.render(
    <Router>
      <ProfileCard
        firebase={firebase}
        firebaseUser={firebaseUser}
        profile={profile}
        match={match}
      />
    </Router>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

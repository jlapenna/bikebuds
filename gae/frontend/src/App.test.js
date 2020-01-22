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

import React from 'react';
import { render, waitForElement } from '@testing-library/react';

import { config } from './config';
import { FirebaseState } from './firebase_util';
import App from './App';

// For mocking the swagger client.
import {
  __setMockClient as __setMockClientForSwagWrapper,
  __reset as __resetSwagWrapper,
} from './SwagWrapper';

jest.mock('./SignInScreen');
jest.mock('./SwagWrapper');

beforeEach(() => {
  __setMockClientForSwagWrapper({
    apis: {
      bikebuds: {
        get_profile: () => Promise.resolve({ body: { signup_complete: true } }),
        get_series: () => Promise.resolve({ body: { properties: {} } }),
        update_client: () => Promise.resolve({ body: {} }),
      },
    },
  });
});

afterEach(() => {
  __resetSwagWrapper();
});

test('Renders unknown without crashing', async () => {
  const firebase = createFirebaseState();
  const { getByTestId } = render(<App firebase={firebase} />);
  expect(getByTestId('unknown-app')).toBeInTheDocument();
});

test('Renders signed-in without crashing', async () => {
  const firebase = createFirebaseState();
  const { getByTestId } = render(<App firebase={firebase} />);

  firebase.auth.changeAuthState(createSignedInState());
  firebase.authNext.changeAuthState(createSignedInState());
  firebase.auth.flush();
  firebase.authNext.flush();

  await waitForElement(() => getByTestId('main'));
});

test('Renders signed-out without crashing', async () => {
  const firebase = createFirebaseState();
  const { getByTestId } = render(<App firebase={firebase} />);

  firebase.auth.changeAuthState(undefined);
  firebase.authNext.changeAuthState(undefined);
  firebase.auth.signOut();
  firebase.authNext.signOut();

  firebase.auth.flush();
  firebase.authNext.flush();

  await waitForElement(() => getByTestId('mock-sign-in-screen'));
});

describe('Signed-in via dev/fakeuser config', () => {
  beforeEach(() => {
    config.is_dev = true;
    config.fake_user = 'jlapenna@gmail.com';
  });

  test('Renders signed-in without crashing', async () => {
    const firebase = new FirebaseState(true /* forTest */);
    const { queryByTestId } = render(<App firebase={firebase} />);
    expect(queryByTestId('main')).toBeInTheDocument();
  });
});

//test('Snapshot test', async () => {
//  const firebase = new FirebaseState(true /* forTest */);
//  const { container, queryByTestId } = render(<App firebase={firebase} />);
//  expect(container).toMatchSnapshot();
//});

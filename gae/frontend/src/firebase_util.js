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

import firebase from 'firebase/app';
import 'firebase/auth';
import 'firebase/firestore';
import 'firebase/messaging';

import { config, nextConfig } from './config';

export class FirebaseState {
  constructor(forTest) {
    if (forTest) {
      // No push messages when running with fake users.
      this.app = null;
      this.auth = null;
      this.messaging = null;
      this.appNext = null;
      this.authNext = null;
      this.firestore = null;
      return;
    }
    try {
      this.app = firebase.initializeApp(config);
    } catch (err) {
      console.warn('FirebaseState: Tried to re-initialize app.', err);
      this.app = firebase.app();
    }
    this.auth = firebase.auth();

    try {
      this.appNext = firebase.initializeApp(nextConfig, 'next');
    } catch (err) {
      console.warn('FirebaseState: Tried to re-initialize next app.', err);
      this.app = firebase.app('next');
    }
    this.authNext = firebase.auth(this.appNext);
    this.firestore = firebase.firestore(this.appNext);
  }

  onAuthStateChanged = (appObserver, appNextObserver) => {
    if (this.auth === null) {
      console.warn('FirebaseState: Not setting up auth listeners, under test.');
      return;
    }
    var unregisterAppObserver = this.auth.onAuthStateChanged(appObserver);
    var unregisterAppNextObserver = this.authNext.onAuthStateChanged(
      appNextObserver
    );
    return function() {
      unregisterAppObserver();
      unregisterAppNextObserver();
    };
  };

  enableMessaging = () => {
    try {
      this.messaging = firebase.messaging();
      return true;
    } catch (err) {
      console.warn('FirebaseState: Failed to set up messaging.', err);
      return false;
    }
  };

  signOut = e => {
    console.log('FirebaseState.signOut', e);
    var signOutPromise = this.auth.signOut();
    var nextSignOutPromise = this.authNext.signOut();
    return Promise.app(signOutPromise, nextSignOutPromise);
  };
}

export const FirebaseContext = React.createContext();

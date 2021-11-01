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
import 'firebase/messaging';

import { firebase_config } from './config';

export class FirebaseState {
  constructor(forTest) {
    if (forTest) {
      // No push messages when running with fake users.
      this.app = null;
      this.auth = null;
      this.messaging = null;
      return;
    }
    try {
      this.app = firebase.initializeApp(firebase_config);
    } catch (err) {
      if (err.code === 'app/duplicate-app') {
        this.app = firebase.app();
      } else {
        console.error('FirebaseState: Failed initializing firebase.', err);
      }
    }
    this.auth = firebase.auth();
  }

  onAuthStateChanged = (appObserver) => {
    if (this.auth === null) {
      console.warn('FirebaseState: Not setting up auth listeners, under test.');
      return;
    }
    return this.auth.onAuthStateChanged(appObserver);
  };

  enableMessaging = () => {
    if (this.messaging) {
      return true;
    }
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
    return this.auth.signOut();
  };
}

export const FirebaseContext = React.createContext();

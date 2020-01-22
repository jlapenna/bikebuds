// https://create-react-app.dev/docs/running-tests#on-your-own-environment
import '@testing-library/jest-dom/extend-expect';

import { FirebaseState } from './firebase_util';
import { config } from './config';

import firebasemock from 'firebase-mock';

// For config.json overrides.
var originalConfig = {};

beforeEach(() => {
  // For config.json overrides.
  Object.assign(originalConfig, config);
  config.isDev = false;
  config.fake_user = '';
});

afterEach(() => {
  // For config.json overrides.
  for (let [key, value] of Object.entries(originalConfig)) {
    config[key] = value;
  }
});

firebasemock.MockMessaging.prototype.onTokenRefresh = fn => {
  return () => true;
};

firebasemock.MockMessaging.prototype.onMessage = fn => {
  return () => true;
};

firebasemock.MockMessaging.prototype.requestPermission = () => {
  return Promise.resolve();
};

firebasemock.MockMessaging.prototype.getToken = () => {
  return Promise.resolve('FCM_TOKEN');
};

var mockAuth = new firebasemock.MockAuthentication();
var mockAuthNext = new firebasemock.MockAuthentication();
var mockFirestore = new firebasemock.MockFirestore();
var mockMessaging = new firebasemock.MockMessaging();

global.createFirebaseState = () => {
  const firebase = new FirebaseState(true /* forTest */);
  firebase.auth = mockAuth;
  firebase.authNext = mockAuthNext;
  firebase.messaging = mockMessaging;
  firebase.firestore = mockFirestore;
  return firebase;
};

global.createSignedInState = () => {
  return {
    uid: 'testUid',
    provider: 'custom',
    token: 'authToken',
    expires: Math.floor(new Date() / 1000) + 24 * 60 * 60,
    getIdTokenResult: () => Promise.resolve({ claims: {}, token: 'XYZ_TOKEN' }),
  };
};

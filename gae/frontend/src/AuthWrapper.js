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

import PropTypes from 'prop-types';
import { Component } from 'react';

import { config } from './config';

class AuthWrapper extends Component {
  static propTypes = {
    firebase: PropTypes.object.isRequired,
    signedInHandler: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      firebaseUser: undefined,
      firebaseToken: undefined,
      firebaseUserNext: undefined,
      firebaseTokenNext: undefined
    };
  }

  _isSignedIn = () => {
    if (
      this.state.firebaseUser === undefined ||
      this.state.firebaseUserNext === undefined
    ) {
      return undefined;
    }
    return !!this.state.firebaseUser && !!this.state.firebaseUserNext;
  };

  componentDidMount() {
    if (config.isDev && config.fakeUser) {
      console.warn('AuthWrapper: Using Fake User.');
      const firebaseUser = {
        displayName: 'Fake User',
        photoUrl: '/logo-round.svg'
      };
      this.setState({
        firebaseUser: firebaseUser,
        firebaseToken: 'XXXXXXXXXXXXXX',
        firebaseUserNext: firebaseUser,
        firebaseTokenNext: 'XXXXXXXXXXXXXX'
      });
      return;
    }

    console.log('AuthWrapper: Using Real Auth');
    this.unregisterAuthObserver = this.props.firebase.onAuthStateChanged(
      this._onAuthStateChangedFn('firebaseUser', 'firebaseToken'),
      this._onAuthStateChangedFn('firebaseUserNext', 'firebaseTokenNext')
    );
  }

  _onAuthStateChangedFn = (firebaseUserKey, firebaseTokenKey) => {
    return firebaseUser => {
      // If we've unmounted before this callback executes, we don't want to
      // update state.
      if (this.unregisterAuthObserver === null) {
        return;
      }
      console.log(
        'AuthWrapper.onAuthStateChanged:',
        firebaseUserKey,
        firebaseUser
      );
      if (!!firebaseUser) {
        firebaseUser.getIdTokenResult().then(idTokenResult => {
          console.log(
            'AuthWrapper.onAuthStateChanged:',
            firebaseUserKey,
            'idTokenResult:',
            idTokenResult
          );
          firebaseUser.admin = !!idTokenResult.claims['admin'];

          var stateUpdate = {};
          stateUpdate[firebaseUserKey] = firebaseUser;
          stateUpdate[firebaseTokenKey] = idTokenResult.token;
          this.setState(stateUpdate);
        });
      } else {
        var stateUpdate = {};
        stateUpdate[firebaseUserKey] = null;
        stateUpdate[firebaseTokenKey] = null;
        this.setState(stateUpdate);
      }
    };
  };

  componentWillUnmount() {
    if (!!this.unregisterAuthObserver) {
      this.unregisterAuthObserver();
      this.unregisterAuthObserver = null;
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (
      prevState.firebaseUser !== this.state.firebaseUser ||
      prevState.firebaseUserNext !== this.state.firebaseUserNext
    ) {
      this.props.signedInHandler(this._isSignedIn());
    }
  }

  render() {
    return this.props.render({
      firebase: this.props.firebase,
      firebaseUser: this.state.firebaseUser,
      firebaseToken: this.state.firebaseToken,
      firebaseUserNext: this.state.firebaseUserNext,
      firebaseTokenNext: this.state.firebaseTokenNext
    });
  }
}
export default AuthWrapper;

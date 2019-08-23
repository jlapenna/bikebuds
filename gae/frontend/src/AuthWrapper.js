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
      isSignedIn: undefined,
      firebaseUser: undefined,
      isSignedInNext: undefined,
      firebaseUserNext: undefined
    };
  }

  _isSignedIn = () => {
    if (this.state.isSignedIn === undefined) {
      return undefined;
    }
    return this.state.isSignedIn;
    //return this.state.isSignedIn && this.state.isSignedInNext;
  };

  componentDidMount() {
    if (config.isDev && config.fakeUser) {
      console.log('AuthWrapper: Warning: Using Fake User.');
      const firebaseUser = {
        displayName: 'Fake User',
        photoUrl: '/logo-round.svg'
      };
      this.setState({
        isSignedIn: true,
        firebaseUser: firebaseUser,
        isSignedInNext: true,
        firebaseUserNext: firebaseUser
      });
      return;
    }

    console.log('AuthWrapper: Using Real Auth');
    this.unregisterAuthObserver = this.props.firebase.onAuthStateChanged(
      firebaseUser => {
        // If we've unmounted before this callback executes, we don't want to
        // update state.
        if (this.unregisterAuthObserver === null) {
          return;
        }
        if (!!firebaseUser) {
          firebaseUser.getIdTokenResult().then(idTokenResult => {
            console.log('AuthWrapper.getIdTokenResult:', idTokenResult);
            firebaseUser.admin = !!idTokenResult.claims['admin'];
            this.setState({
              isSignedIn: !!firebaseUser,
              firebaseUser: firebaseUser
            });
          });
        }
      },
      firebaseUser => {
        // If we've unmounted before this callback executes, we don't want to
        // update state.
        if (this.unregisterAuthObserver === null) {
          return;
        }
        if (!!firebaseUser) {
          firebaseUser.getIdTokenResult().then(idTokenResult => {
            console.log('AuthWrapper.getIdTokenResultNext:', idTokenResult);
            firebaseUser.admin = !!idTokenResult.claims['admin'];
            this.setState({
              isSignedInNext: !!firebaseUser,
              firebaseUserNext: firebaseUser
            });
          });
        }
      }
    );
  }

  componentWillUnmount() {
    if (!!this.unregisterAuthObserver) {
      this.unregisterAuthObserver();
      this.unregisterAuthObserver = null;
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (
      prevState.isSignedIn !== this.state.isSignedIn ||
      prevState.isSignedInNext !== this.state.isSignedInNext
    ) {
      this.props.signedInHandler(this._isSignedIn());
    }
  }

  render() {
    return this.props.render({
      firebase: this.props.firebase,
      firebaseUser: this.state.firebaseUser,
      firebaseUserNext: this.state.firebaseUserNext
    });
  }
}
export default AuthWrapper;

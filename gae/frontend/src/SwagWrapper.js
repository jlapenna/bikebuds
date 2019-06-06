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

import firebase from 'firebase/app';
import 'firebase/auth';

import Swagger from 'swagger-client';

import { config } from './config';

const bikebudsDiscoveryUrl = config.api3Url + '/swagger.json';

class SwagWrapper extends Component {
  constructor(props) {
    super(props);
    this.state = {
      authDict: undefined,
      clientLoaded: undefined,
      client: undefined,
      failed: false
    };
  }

  componentDidMount() {
    // Listen for sign-in, sign-out
    if (config.isDev && config.fakeUser) {
      this.setState({ authDict: { access_token: 'XXXXXXXXXXXXXXXXXXX' } });
      return;
    }
    this.unregisterAuthObserver = firebase.auth().onAuthStateChanged(user => {
      user
        .getIdToken(true)
        .then(idToken => {
          this.setState({ authDict: { access_token: idToken } });
        })
        .catch(err => {
          console.log('SwagWrapper.getIdToken: failed', err);
          this.setState({ failed: true });
        });
    });
  }

  componentWillUnmount() {
    if (!!this.unregisterAuthObserver) {
      this.unregisterAuthObserver();
      this.unregisterAuthObserver = null;
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (prevState.failed !== this.state.failed && this.state.failed) {
      // Notify the parent whenever a failure occurs, because we never set
      // failed false, this will only happen once.
      if (this.props.onFailed !== undefined) {
        this.props.onFailed();
      }
    }
    if (this.state.failed) {
      console.log('SwagWrapper.componentDidUpdate: permanently failed.');
      return;
    }
    if (
      this.state.authDict !== prevState.authDict ||
      this.state.clientLoaded !== prevState.clientLoaded
    ) {
      if (this.state.authDict !== undefined && this.state.clientLoaded) {
        //apiClient.setToken(this.state.authDict);
        //apiClient.setApiKey(config.apiKey);
        this.props.onReady(this.state.client);
      }
    }
    if (this.state.authDict !== prevState.authDict) {
      if (
        this.state.authDict !== undefined &&
        this.state.clientLoaded === undefined
      ) {
        console.log('SwagWrapper: Loading client');
        this.setState({ clientLoaded: false });
        Swagger({
          url: bikebudsDiscoveryUrl,
          authorizations: {
            api_key: config.apiKey,
            firebase: { token: this.state.authDict }
          }
        }).then(client => {
          console.log('SwagWrapper: Loaded client: ', client);
          this.setState({ clientLoaded: true, client: client });
        });
      }
    }
  }

  render() {
    return <div className="SwagWrapper" />;
  }
}
export default SwagWrapper;

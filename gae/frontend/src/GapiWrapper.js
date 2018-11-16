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

import React, { Component } from 'react';

import firebase from 'firebase/app';
import 'firebase/auth';

import { config, backendConfig } from './Config';

const bikebudsDiscoveryUrl = backendConfig.apiHostUrl + '/bikebuds-v1.discovery';

class GapiWrapper extends Component {
  constructor(props) {
    super(props);
    this.state = {
      clientLoaded: false,
      bikebudsDiscovery: undefined,
      bikebudsLoaded: undefined,
      bikebudsReady: false,
      authDict: undefined,
    }
    this.onGapiLoaded = this.onGapiLoaded.bind(this);
  }

  /** Load the gapi client after the library is loaded. */
  onGapiLoaded() {
    window.gapi.load('client', () => {
      console.log('GapiWrapper.onClientLoaded', window.gapi.client);
      this.setState({clientLoaded: true});
    });
  }

  /**
   * @inheritDoc
   */
  componentDidMount() {
    console.log('GapiWrapper.componentDidMount');

    // Listen for sign-in, sign-out
    this.unregisterAuthObserver = firebase.auth().onAuthStateChanged((user) => {
      user.getIdToken(true).then((idToken) => {
        this.setState({authDict: {access_token: idToken}});
      });
    });

    // Load up the google-api library and a client.
    const gapiScript = document.createElement('script');
    gapiScript.src = 'https://apis.google.com/js/api.js?onload=onGapiLoaded';
    window.onGapiLoaded = this.onGapiLoaded;
    document.body.appendChild(gapiScript)

    // Fetch a discovery doc.
    fetch(bikebudsDiscoveryUrl).then((discoveryResponse) => {
      discoveryResponse.json().then((bikebudsDiscovery) => {
        this.setState({bikebudsDiscovery: bikebudsDiscovery});
      });
    });
  };

  /**
   * @inheritDoc
   */
  componentWillUnmount() {
    console.log('GapiWrapper: componentWillUnmount');
    this.unregisterAuthObserver();
  };

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('GapiWrapper.componentDidUpdate', prevState, this.state);
    if ((this.state.clientLoaded !== prevState.clientLoaded)
      || (this.state.bikebudsDiscovery !== prevState.bikebudsDiscovery)) {
      if (this.state.clientLoaded
        && this.state.bikebudsDiscovery !== undefined
        && this.bikebudsLoaded === undefined) {
        this.setState({bikebudsLoaded: false});
        window.gapi.client.load(this.state.bikebudsDiscovery).then(() => {
          this.setState({bikebudsLoaded: true});
        });
      };
    };
    if ((this.state.authDict !== prevState.authDict)
      || (this.state.bikebudsLoaded !== prevState.bikebudsLoaded)) {
      if ((this.state.authDict !== undefined)
        && this.state.bikebudsLoaded) {
        window.gapi.client.setToken(this.state.authDict);
        window.gapi.client.setApiKey(config.apiKey);
        this.setState({bikebudsReady: true});
        console.log('GapiWrapper: Ready');
        this.props.onReady();
      };
    };
  };

  /**
   * @inheritDoc
   */
  render() {
    return (
      <div className="GapiWrapper" />
    );
  };
}

export default GapiWrapper;

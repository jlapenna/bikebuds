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

import PropTypes from 'prop-types';
import React, { Component } from 'react';

import { config } from './config';

class FcmManager extends Component {
  static propTypes = {
    firebase: PropTypes.object.isRequired,
    apiClient: PropTypes.object.isRequired,
    onMessage: PropTypes.func,
    onReady: PropTypes.func,
  };

  constructor(props) {
    super(props);
    this.state = {
      registered: undefined,
      updated: undefined,
      fcmToken: localStorage.getItem('fcmToken'),
      client: undefined,
    };

    this.tokenListener = null;
    this.messageListener = null;
  }

  registerFcm = () => {
    if (config.vapidKey !== undefined) {
      this.props.firebase.messaging.usePublicVapidKey(config.vapidKey);
    }
    this.props.firebase.messaging
      .requestPermission()
      .then(() => {
        return this.props.firebase.messaging.getToken();
      })
      .then(token => {
        localStorage.setItem('fcmToken', token);
        this.setState({
          fcmToken: token,
          registered: true,
        });
      })
      .catch(error => {
        console.warn('FcmManager: Error: ', error);
        localStorage.setItem('fcmToken', null);
        this.setState({
          fcmToken: null,
        });
      });
  };

  handleUpdateClient = response => {
    if (response.body === undefined) {
      return;
    }
    this.setState({
      client: response.body.client,
      updated: true,
    });
    if (this.props.onReady !== undefined) {
      this.props.onReady(response.body.client);
    }
  };

  componentDidMount() {
    if (config.isDev && config.fakeUser) {
      // No push messages when running with fake users.
      return;
    }
    // onTokenRefresh is only called when firebase gives the app a new token,
    // which isn't every reload, but during an "app install" so to speak.
    this.tokenListener = this.props.firebase.messaging.onTokenRefresh(token => {
      console.log('FcmManager.onTokenRefresh:', token);
      localStorage.setItem('fcmToken', token);
      this.setState({
        fcmToken: token,
      });
    });
    this.messageListener = this.props.firebase.messaging.onMessage(payload => {
      console.log('FcmManager.onMessage', payload);
      if (this.props.onMessage !== undefined) {
        this.props.onMessage(payload);
      }
    });

    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  componentWillUnmount() {
    if (this.tokenListener != null) {
      this.tokenListener();
    }
    if (this.messageListener != null) {
      this.messageListener();
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (config.isDev && config.fakeUser) {
      // No push messages when running with fake users.
      return;
    }
    if (this.state.registered === undefined) {
      this.setState({
        registered: false,
      });
      this.registerFcm();
    }

    if (
      this.state.fcmToken !== prevState.fcmToken &&
      this.state.fcmToken != null
    ) {
      this.props.apiClient.bikebuds
        .update_client({
          payload: {
            active: true,
            token: this.state.fcmToken,
            type: 'WEB',
          },
        })
        .then(this.handleUpdateClient);
    }
  }

  render() {
    return <div className="FcmManager" />;
  }
}
export default FcmManager;

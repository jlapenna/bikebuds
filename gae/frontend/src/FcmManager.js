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

class FcmWrapper extends Component {
  static propTypes = {
    firebase: PropTypes.object.isRequired,
    gapiReady: PropTypes.bool.isRequired,
    onMessage: PropTypes.func,
    onReady: PropTypes.func
  };

  constructor(props) {
    super(props);
    this.state = {
      monitored: undefined,
      registered: undefined,
      updated: undefined,
      fcmToken: undefined,
      client: undefined
    };

    this.tokenListener = null;
    this.messageListener = null;
  }

  registerFcm = () => {
    console.log('FcmWrapper.registerFcm');
    if (config.vapidKey !== undefined) {
      this.props.firebase.messaging.usePublicVapidKey(config.vapidKey);
    }
    this.props.firebase.messaging
      .requestPermission()
      .then(() => {
        console.log('FcmWrapper.registerFcm: got token');
        return this.props.firebase.messaging.getToken();
      })
      .then(token => {
        console.log('FcmWrapper.registerFcm: token set');
        this.setState({
          fcmToken: token,
          registered: true
        });
      })
      .catch(error => {
        this.setState({
          fcmToken: null
        });
        if (error.code === 'messaging/permission-blocked') {
          console.log(
            'FcmWrapper: Please Unblock Notification Request Manually'
          );
        } else {
          console.log('FcmWrapper: Error Occurred', error);
        }
      });
  };

  updateClientState = response => {
    console.log('FcmWrapper.updateClientState:', response.result);
    if (response.result === undefined) {
      return;
    }
    this.setState({
      client: response.result.client,
      updated: true
    });
    if (this.props.onReady !== undefined) {
      this.props.onReady(response.result.client);
    }
  };

  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.tokenListener = this.props.firebase.messaging.onTokenRefresh(() => {
      console.log('FcmWrapper.onTokenRefresh');
      this.registerFcm();
    });
    this.messageListener = this.props.firebase.messaging.onMessage(payload => {
      console.log('FcmWrapper.onMessage', payload);
      if (this.props.onMessage !== undefined) {
        this.props.onMessage(payload);
      }
    });
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
    console.log('FcmWrapper.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.monitored === undefined) {
      console.log('FcmWrapper.componentDidUpdate: monitoring');
      this.setState({
        monitored: false
      });
    }

    if (
      this.props.gapiReady &&
      this.state.fcmToken === undefined &&
      this.state.registered === undefined
    ) {
      console.log('FcmWrapper.componentDidUpdate: register');
      this.setState({
        registered: false
      });
      this.registerFcm();
    }

    if (
      this.props.gapiReady &&
      this.state.fcmToken &&
      this.state.updated === undefined
    ) {
      this.setState({
        updated: false
      });
      console.log('FcmWrapper.componentDidUpdate: update_client');
      window.gapi.client.bikebuds
        .update_client({
          client: { id: this.state.fcmToken }
        })
        .then(this.updateClientState);
    }
  }

  render() {
    return <div className="FcmWrapper" />;
  }
}
export default FcmWrapper;

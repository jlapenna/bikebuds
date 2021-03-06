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

import Swagger from 'swagger-client';

import { config, firebase_config } from './config';

const bikebudsDiscoveryUrl = config.api_url + '/swagger.json';

class SwagWrapper extends Component {
  static propTypes = {
    firebaseToken: PropTypes.string.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      clientLoaded: undefined,
      client: undefined,
    };
  }

  componentDidMount() {
    this._mounted = true;
    const authDict = { access_token: this.props.firebaseToken };
    this._swaggerLoader = Swagger({
      url: bikebudsDiscoveryUrl,
      authorizations: {
        api_key: firebase_config.apiKey,
        firebase: { token: authDict },
      },
    }).then(client => {
      if (this._mounted) {
        this.setState({ clientLoaded: true, client: client });
        this.props.onReady(client);
      }
    });
  }

  componentWillUnmount() {
    this._mounted = false;
  }

  render() {
    return <div className="SwagWrapper" />;
  }
}
export default SwagWrapper;

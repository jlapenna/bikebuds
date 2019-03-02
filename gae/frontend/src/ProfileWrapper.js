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

export default class ProfileWrapper extends Component {
  static propTypes = {
    gapiReady: PropTypes.bool.isRequired,
    onProfileReady: PropTypes.func.isRequired,
    profile: PropTypes.object
  };

  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      profile: props.profile
    };
  }

  handleProfile = response => {
    console.log('ProfileWrapper.handleProfile:', response.result);
    if (response.result === undefined) {
      return;
    }
    this.setState({
      profile: response.result
    });
    this.props.onProfileReady(response.result);
  };

  /**
   * @inheritDoc
   */
  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ProfileWrapper.componentDidUpdate', prevProps);
    if (this.props.gapiReady && !this.state.fetched) {
      this.setState({ fetched: true });
      window.gapi.client.bikebuds.get_profile().then(this.handleProfile);
    }
  }

  /**
   * @inheritDoc
   */
  render() {
    console.log('ProfileWrapper.render', this.state.profile);
    return <div className="ProfileWrapper" />;
  }
}

export const ProfileContext = React.createContext();

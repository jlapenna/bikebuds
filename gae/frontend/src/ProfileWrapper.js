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
import React from 'react';

export class ProfileState {
  constructor(onUpdated) {
    this._onUpdated = onUpdated;
    this.fetched = false;
  }

  update(result) {
    this.fetched = true;
    this.signup_complete = result.signup_complete;
    this.user = result.user;
    this.athlete = result.athlete;
    this._onUpdated(this);
  }

  updatePreferences(result) {
    this.user.properties.preferences = result;
    this._onUpdated(this);
  }
}

export default class ProfileWrapper extends React.Component {
  static propTypes = {
    apiClient: PropTypes.object.isRequired,
    profile: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
    };
  }

  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.apiClient && !this.state.fetched) {
      this.setState({ fetched: true });
      this.props.apiClient.bikebuds.get_profile({}).then(response => {
        this.props.profile.update(response.body);
      });
    }
  }

  render() {
    return null;
  }
}

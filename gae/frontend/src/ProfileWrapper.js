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

import { Redirect, Route } from 'react-router-dom';

export class ProfileState {
  constructor(onUpdated) {
    this._onUpdated = onUpdated;
    this.fetched = false;
  }

  update(result) {
    this.signup_complete = result.signup_complete;
    this.user = result.user;
    this.athlete = result.athlete;
    this.fetched = true;
    this._onUpdated(this);
  }

  updatePreferences(result) {
    this.user.properties.preferences = result;
    this._onUpdated(this);
  }
}

export default class ProfileWrapper extends React.Component {
  static propTypes = {
    bikebudsApi: PropTypes.object.isRequired,
    match: PropTypes.object.isRequired,
    profileState: PropTypes.object.isRequired,
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
    if (this.props.bikebudsApi && !this.state.fetched) {
      this.setState({ fetched: true });
      this.props.bikebudsApi.get_profile({}).then(response => {
        this.props.profileState.update(response.body);
      });
    }
  }

  render() {
    if (
      this.props.profileState.fetched &&
      !this.props.profileState.signup_complete
    ) {
      return (
        <Route>
          <Redirect to={`${this.props.match.url}signup`} />
        </Route>
      );
    } else {
      return null;
    }
  }
}

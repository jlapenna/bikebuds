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

import { createRequest } from './bikebuds_api';

class ActivitiesWrapper extends Component {
  static propTypes = {
    apiClient: PropTypes.object.isRequired,
    onResponse: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      response: undefined
    };
  }

  handleUpdateRequestState = response => {
    console.log('ActivitiesWrapper.handleUpdateRequestState:', response.body);
    this.setState({
      response: response
    });
    this.props.onResponse(response);
  };

  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ActivitiesWrapper.componentDidUpdate', prevProps);
    if (
      this.props.apiClient &&
      !this.state.fetched &&
      this.state.response === undefined
    ) {
      this.setState({ fetched: true });
      this.props.apiClient.bikebuds
        .get_activities(createRequest())
        .then(this.handleUpdateRequestState);
    }
  }

  render() {
    console.log('ActivitiesWrapper.render', this.state.response);
    return <div className="ActivitiesWrapper" />;
  }
}
export default ActivitiesWrapper;

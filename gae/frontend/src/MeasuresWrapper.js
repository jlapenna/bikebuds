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
import React, { Component } from 'react';

import moment from 'moment';

import { readableWeight } from './convert';

class MeasuresWrapper extends Component {
  static propTypes = {
    profile: PropTypes.object.isRequired,
    render: PropTypes.func.isRequired,
  };

  constructor(props) {
    super(props);
    this._mounted = false;
    this.state = {
      fetched: false,
      measures: undefined,
    };
  }

  handleSeries = response => {
    if (!this._mounted) {
      return;
    }
    var measures = [];
    if (!!response.body && response.body.properties.measures !== undefined) {
      measures = response.body.properties.measures;
    }
    for (var measure in measures) {
      measures[measure].date = moment.utc(measures[measure].date).format('x');
      if (measures[measure].weight !== undefined) {
        measures[measure].weight = readableWeight(
          measures[measure].weight,
          this.props.profile
        );
      }
    }
    this.setState({
      measures: measures,
    });
  };

  componentDidMount() {
    this._mounted = true;
    if (!this.state.fetched) {
      this.setState({ fetched: true });
      this.props.apiClient.bikebuds
        .get_series({ filter: 'weight' })
        .then(this.handleSeries);
    }
  }

  componentWillUnmount() {
    this._mounted = false;
  }

  render() {
    return <React.Fragment>{this.props.render(this.state)}</React.Fragment>;
  }
}

export default MeasuresWrapper;

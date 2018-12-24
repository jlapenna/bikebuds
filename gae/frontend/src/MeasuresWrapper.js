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


class MeasuresWrapper extends Component {
  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      measures: undefined,
    }
  }

  updateMeasuresState = (response) => {
    console.log('MeasuresWrapper.updateMeasuresState:', response);
    var measures = [];
    if (response.result.series !== undefined
      && response.result.series.measures !== undefined) {
      measures = response.result.series.measures;
    }
    this.setState({
      measures: measures,
    });
    this.props.onMeasuresReady(measures);
  }

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
    console.log('MeasuresWrapper.componentDidUpdate', prevProps);
    if (this.props.gapiReady
      && !this.state.fetched
      && this.state.measures === undefined) {
      this.setState({fetched: true});
      window.gapi.client.bikebuds.get_series().then(this.updateMeasuresState);
    }
  }

  /**
   * @inheritDoc
   */
  render() {
    return (
      <div className="MeasuresWrapper" />
    );
  };
}

MeasuresWrapper.propTypes = {
  onMeasuresReady: PropTypes.func.isRequired,
}
export default MeasuresWrapper;

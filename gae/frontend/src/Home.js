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

import Grid from '@material-ui/core/Grid';

import ActivityListCard from './ActivityListCard';
import MeasuresCard from './MeasuresCard';
import MeasuresWrapper from './MeasuresWrapper';

class Home extends Component {
  constructor(props) {
    super(props);
    this.state = {}
  }

  onMeasuresReady = (measures) => {
    console.log('Home.onMeasuresReady', measures);
    this.setState({measures: measures});
  }

  render() {
    return (
      <div>
        <MeasuresWrapper
          gapiReady={this.props.gapiReady}
          onMeasuresReady={this.onMeasuresReady}
        />
        <Grid container spacing={24}>
          <Grid item xs={12}>
            <ActivityListCard
              gapiReady={this.props.gapiReady} />
          </Grid>
          <Grid item xs={12}>
            <MeasuresCard
              gapiReady={this.props.gapiReady}
              measures={this.state.measures}
              title="Daily"
              intervalUnit="d" intervalFormat="MMM D" intervalCount="365"
            />
          </Grid>
          <Grid item xs={12}>
            <MeasuresCard
              gapiReady={this.props.gapiReady}
              measures={this.state.measures}
              title="Weekly"
              intervalUnit="w" intervalFormat="MMM D" intervalCount="52"
            />
          </Grid>
          <Grid item xs={12}>
            <MeasuresCard
              gapiReady={this.props.gapiReady}
              measures={this.state.measures}
              title="All Time"
              intervalUnit="M" intervalFormat="MMM 'YY" intervalCount="120"
            />
          </Grid>
        </Grid>
      </div>
    );
  }
}

export default Home;

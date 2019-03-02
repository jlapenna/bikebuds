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

import Grid from '@material-ui/core/Grid';

import ActivityListCard from './ActivityListCard';
import ActivitiesWrapper from './ActivitiesWrapper';
import MeasuresCard from './MeasuresCard';
import MeasuresWrapper from './MeasuresWrapper';

class Home extends Component {
  static propTypes = {
    gapiReady: PropTypes.bool.isRequired,
    profile: PropTypes.object
  };

  constructor(props) {
    super(props);
    this.state = {};
  }

  handleActivitiesResponse = response => {
    console.log('Home.onActivitiesReady', response);
    this.setState({
      activities: response.result.activities
    });
  };

  handleMeasuresReady = measures => {
    console.log('Home.handleMeasuresReady', measures);
    this.setState({ measures: measures });
  };

  render() {
    return (
      <div>
        <MeasuresWrapper
          profile={this.props.profile}
          gapiReady={this.props.gapiReady}
          onMeasuresReady={this.handleMeasuresReady}
        />
        <Grid container spacing={24}>
          <Grid item xs={12} lg={8}>
            <ActivitiesWrapper
              gapiReady={this.props.gapiReady}
              onResponse={this.handleActivitiesResponse}
            />
            <ActivityListCard
              gapiReady={this.props.gapiReady}
              profile={this.props.profile}
              activities={this.state.activities}
              showDate={true}
            />
          </Grid>
          <Grid item xs={12} lg={4}>
            <MeasuresCard
              gapiReady={this.props.gapiReady}
              profile={this.props.profile}
              measures={this.state.measures}
              title="Weight"
              intervalUnit="d"
              intervalFormat="MMM D"
              intervalCount="30"
            />
          </Grid>
          <Grid item xs={12}>
            <MeasuresCard
              gapiReady={this.props.gapiReady}
              profile={this.props.profile}
              measures={this.state.measures}
              title="Historical Weight"
              intervalUnit="M"
              intervalFormat="MMM 'YY"
              intervalCount="120"
            />
          </Grid>
        </Grid>
      </div>
    );
  }
}
export default Home;

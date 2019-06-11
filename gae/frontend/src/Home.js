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

import ActivitiesListCard from './ActivitiesListCard';
import ActivitiesWrapper from './ActivitiesWrapper';
import MeasuresCard from './MeasuresCard';
import MeasuresSummaryCard from './MeasuresSummaryCard';
import MeasuresWrapper from './MeasuresWrapper';

class Home extends Component {
  static propTypes = {
    apiClient: PropTypes.object.isRequired,
    profile: PropTypes.object
  };

  constructor(props) {
    super(props);
    this.state = {};
  }

  handleActivitiesResponse = response => {
    console.log('Home.onActivitiesReady', response);
    this.setState({
      activities: response.body
    });
  };

  render() {
    return (
      <div>
        <MeasuresWrapper
          profile={this.props.profile}
          apiClient={this.props.apiClient}
          render={wrapperState => (
            <Grid container spacing={24}>
              <Grid item xs={12} lg={8}>
                <ActivitiesWrapper
                  apiClient={this.props.apiClient}
                  onResponse={this.handleActivitiesResponse}
                />
                <ActivitiesListCard
                  apiClient={this.props.apiClient}
                  profile={this.props.profile}
                  activities={this.state.activities}
                  showDate={true}
                />
              </Grid>
              <Grid item xs={12} lg={4}>
                <MeasuresSummaryCard
                  profile={this.props.profile}
                  measures={wrapperState.measures}
                />
              </Grid>
              <Grid item xs={12}>
                <MeasuresCard
                  apiClient={this.props.apiClient}
                  profile={this.props.profile}
                  measures={wrapperState.measures}
                  title="Historical Weight"
                  intervalUnit="M"
                  intervalFormat="MMM 'YY"
                  intervalCount="120"
                  tooltipFormat="MMM 'YY"
                />
              </Grid>
            </Grid>
          )}
        />
      </div>
    );
  }
}
export default Home;

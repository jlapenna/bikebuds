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

import ActivitiesCard from './ActivitiesCard';
import MeasuresCard from './MeasuresCard';

class Home extends Component {
  render() {
    return (
      <div>
        <Grid container spacing={24}>
          <Grid item xs={12}>
            <MeasuresCard gapiReady={this.props.gapiReady}
              title="Daily"
              intervalUnit="d" intervalFormat="MMM D" intervalCount="365"
            />
          </Grid>
          <Grid item xs={12}>
            <MeasuresCard gapiReady={this.props.gapiReady}
              title="Weekly"
              intervalUnit="w" intervalFormat="MMM D" intervalCount="52"
            />
          </Grid>
          <Grid item xs={12}>
            <MeasuresCard gapiReady={this.props.gapiReady}
              title="Yearly"
              intervalUnit="Y" intervalFormat="'YY" intervalCount="10"
            />
          </Grid>
          <Grid item xs={12}>
            <ActivitiesCard
              gapiReady={this.props.gapiReady} />
          </Grid>
        </Grid>
      </div>
    );
  }
}

export default Home;

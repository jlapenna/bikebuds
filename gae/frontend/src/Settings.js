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
import { createStyles, withStyles } from '@material-ui/core/styles';

import PreferencesCard from './PreferencesCard';
import ProfileCard from './ProfileCard';
import ServiceCard from './ServiceCard';

class Settings extends Component {
  static styles = createStyles({
    root: {
      flexGrow: 1,
    },
  });

  static propTypes = {
    bikebudsApi: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object,
    match: PropTypes.object,
    profile: PropTypes.object,
  };

  render() {
    return (
      <Grid className={this.props.classes.root} container spacing={3}>
        <Grid item xs={12} sm={12}>
          <ProfileCard
            firebase={this.props.firebase}
            firebaseUser={this.props.firebaseUser}
            bikebudsApi={this.props.bikebudsApi}
            match={this.props.match}
            profile={this.props.profile}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <ServiceCard
            firebase={this.props.firebase}
            serviceName={'fitbit'}
            bikebudsApi={this.props.bikebudsApi}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <ServiceCard
            firebase={this.props.firebase}
            serviceName={'strava'}
            bikebudsApi={this.props.bikebudsApi}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <ServiceCard
            firebase={this.props.firebase}
            serviceName={'withings'}
            bikebudsApi={this.props.bikebudsApi}
          />
        </Grid>
        <Grid item xs={12}>
          <PreferencesCard
            bikebudsApi={this.props.bikebudsApi}
            profile={this.props.profile}
          />
        </Grid>
      </Grid>
    );
  }
}
export default withStyles(Settings.styles)(Settings);

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

import PreferencesCard from './PreferencesCard';
import ProfileCard from './ProfileCard';
import ServiceCard from './ServiceCard';

class Settings extends Component {
  static propTypes = {
    apiClient: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object,
    profile: PropTypes.object
  };

  render() {
    return (
      <div>
        <Grid container spacing={24} justify="space-evenly" alignItems="center">
          <Grid item xs={12} sm={12}>
            <ProfileCard
              firebaseUser={this.props.firebaseUser}
              apiClient={this.props.apiClient}
              profile={this.props.profile}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <PreferencesCard
              firebaseUser={this.props.firebaseUser}
              apiClient={this.props.apiClient}
              profile={this.props.profile}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <ServiceCard
              serviceName="fitbit"
              apiClient={this.props.apiClient}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <ServiceCard
              serviceName="strava"
              apiClient={this.props.apiClient}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <ServiceCard
              serviceName="withings"
              apiClient={this.props.apiClient}
            />
          </Grid>
        </Grid>
      </div>
    );
  }
}
export default Settings;

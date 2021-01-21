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

import { Redirect, Route, Switch } from 'react-router-dom';

import Admin from './Admin';
import Club from './Club';
import CompareSegments from './CompareSegments';
import Events from './Events';
import Health from './Health';
import Settings from './Settings';
import SpinnerScreen from './SpinnerScreen';

export default class MainContent extends React.Component {
  static propTypes = {
    match: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
    adminApi: PropTypes.object,
    bikebudsApi: PropTypes.object,
    profile: PropTypes.object,
  };

  render() {
    if (!this.props.profile.fetched) {
      return <SpinnerScreen>Loading profile...</SpinnerScreen>;
    }
    if (!this.props.bikebudsApi) {
      return <SpinnerScreen>Connecting to bikebuds...</SpinnerScreen>;
    }
    return (
      <Switch>
        {this.props.firebaseUser.roleUser && (
        <Route
          path={`${this.props.match.path}club/:club_id`}
          render={props => (
            <Club
              clubId={Number(props.match.params.club_id)}
              bikebudsApi={this.props.bikebudsApi}
              profile={this.props.profile}
            />
          )}
        />)}
        {this.props.firebaseUser.roleUser && (
        <Route
          path={`${this.props.match.path}activities`}
          exact
          render={props => (
            <Events
              firebase={this.props.firebase}
              bikebudsApi={this.props.bikebudsApi}
            />
          )}
        />)}
        {this.props.firebaseUser.roleUser && (
        <Route
          path={`${this.props.match.path}compare_segments`}
          exact
          render={props => (
            <CompareSegments
              profile={this.props.profile}
              bikebudsApi={this.props.bikebudsApi}
            />
          )}
        />)}
        {this.props.firebaseUser.roleUser && (
        <Route
          path={`${this.props.match.path}settings`}
          render={props => (
            <Settings
              bikebudsApi={this.props.bikebudsApi}
              firebase={this.props.firebase}
              firebaseUser={this.props.firebaseUser}
              match={this.props.match}
              profile={this.props.profile}
            />
          )}
        />)}
        {this.props.firebaseUser.roleUser && (
        <Route
          path={`${this.props.match.path}health`}
          exact
          render={props => (
            <Health
              bikebudsApi={this.props.bikebudsApi}
              profile={this.props.profile}
            />
          )}
        />)}
        {this.props.firebaseUser.roleAdmin && (
          <Route
            path={`${this.props.match.path}admin`}
            render={props => (
              <Admin
                adminApi={this.props.adminApi}
                bikebudsApi={this.props.bikebudsApi}
                firebase={this.props.firebase}
                firebaseUser={this.props.firebaseUser}
              />
            )}
          />
        )}
        <Route render={props => <Redirect to="/activities" />} />
      </Switch>
    );
  }
}

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

import Club from './Club';
import Events from './Events';
import Home from './Home';
import Settings from './Settings';
import Signup from './Signup';

export default class MainContent extends React.Component {
  static propTypes = {
    match: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
    apiClient: PropTypes.object.isRequired,
    profile: PropTypes.object,
  };

  render() {
    console.log(
      'MainContent.render: ',
      this.props.match.path,
      this.props.profile
    );
    if (!this.props.profile.fetched) {
      console.log('MainContent.render: no profile');
      return null;
    }
    if (!this.props.profile.signup_complete) {
      return (
        <Route>
          <Redirect to={`${this.props.match.url}signup`} />
        </Route>
      );
    }

    return (
      <Switch>
        <Route
          path={`${this.props.match.path}club/:club_id`}
          render={props => (
            <Club
              clubId={Number(props.match.params.club_id)}
              apiClient={this.props.apiClient}
              profile={this.props.profile}
            />
          )}
        />
        <Route
          path={`${this.props.match.path}events`}
          exact
          render={props => (
            <Events
              firebase={this.props.firebase}
              apiClient={this.props.apiClient}
            />
          )}
        />
        <Route
          path={`${this.props.match.path}settings`}
          render={props => (
            <Settings
              apiClient={this.props.apiClient}
              firebaseUser={this.props.firebaseUser}
              match={this.props.match}
              profile={this.props.profile}
            />
          )}
        />
        <Route
          path={`${this.props.match.path}signup`}
          exact
          render={props => <Signup />}
        />
        <Route
          path={`${this.props.match.path}`}
          exact
          render={props => (
            <Home
              apiClient={this.props.apiClient}
              profile={this.props.profile}
            />
          )}
        />
      </Switch>
    );
  }
}

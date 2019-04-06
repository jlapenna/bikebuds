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
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
    gapiReady: PropTypes.bool.isRequired,
    profile: PropTypes.object
  };

  render() {
    console.log('MainContent.render: ', this.props.profile);
    if (!this.props.profile.fetched) {
      console.log('MainContent.render: no profile');
      return null;
    }
    if (!this.props.profile.signup_complete) {
      return (
        <Route>
          <Redirect to="/signup" />
        </Route>
      );
    }

    return (
      <Switch>
        <Route
          path="/club/:club_id"
          render={thinger => (
            <Club
              clubId={Number(thinger.match.params.club_id)}
              gapiReady={this.props.gapiReady}
              profile={this.props.profile}
            />
          )}
        />
        <Route
          path="/"
          exact
          render={() => (
            <Home
              gapiReady={this.props.gapiReady}
              profile={this.props.profile}
            />
          )}
        />
        <Route
          path="/events"
          exact
          render={() => (
            <Events
              firebase={this.props.firebase}
              gapiReady={this.props.gapiReady}
            />
          )}
        />
        <Route
          path="/settings"
          exact
          render={() => (
            <Settings
              gapiReady={this.props.gapiReady}
              firebaseUser={this.props.firebaseUser}
              profile={this.props.profile}
            />
          )}
        />
        <Route path="/signup" exact render={() => <Signup />} />
        <Route>
          <Redirect to="/" />
        </Route>
      </Switch>
    );
  }
}

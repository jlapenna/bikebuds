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

import {
  Redirect,
  BrowserRouter as Router,
  Route,
  Switch,
} from 'react-router-dom';

import CssBaseline from '@material-ui/core/CssBaseline';

import { MuiThemeProvider } from '@material-ui/core/styles';

import 'typeface-roboto';

import theme from './theme';

import { FirebaseState } from './firebase_util';

import AuthWrapper from './AuthWrapper';
import Embed from './Embed';
import Main from './Main';
import Privacy from './Privacy';
import SignInScreen from './SignInScreen';
import StandaloneSignup from './StandaloneSignup';
import ToS from './ToS';

export class SignedInApp extends Component {
  static propTypes = {
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
    firebaseToken: PropTypes.string.isRequired,
  };

  render() {
    console.log('App.SignedInApp.render');
    return (
      <div data-testid="signed-in-app">
        <Router>
          <Switch>
            <Route
              path="/signup"
              render={routeProps => (
                <StandaloneSignup {...this.props} match={routeProps.match} />
              )}
            />
            <Route
              path="/embed/"
              render={routeProps => (
                <Embed {...this.props} match={routeProps.match} />
              )}
            />
            <Route path="/signin">
              <Redirect to="/" />
            </Route>
            <Route
              path="/"
              render={routeProps => (
                <Main {...this.props} match={routeProps.match} />
              )}
            />
            <Route>
              <Redirect to="/" />
            </Route>
          </Switch>
        </Router>
      </div>
    );
  }
}

export class SignedOutApp extends Component {
  static propTypes = {
    firebase: PropTypes.object.isRequired,
  };

  render() {
    console.log('App.SignedOutApp.render');
    return (
      <div data-testid="signed-out-app">
        <Router>
          <Switch>
            <Route
              path="/signin"
              render={props => (
                <SignInScreen
                  firebase={this.props.firebase}
                  match={props.match}
                />
              )}
            />
            <Route>
              <Redirect to="/signin" />
            </Route>
          </Switch>
        </Router>
      </div>
    );
  }
}

export class MainApp extends Component {
  static propTypes = {
    firebase: PropTypes.object.isRequired,
  };
  constructor(props) {
    super(props);
    this.state = {
      isSignedIn: undefined,
    };
  }

  handleSignedIn = isSignedIn => {
    console.log('App.MainApp.handleSignedIn:', isSignedIn);
    this.setState({ isSignedIn: isSignedIn });
  };

  render() {
    console.log('App.MainApp.render');
    return (
      <div data-testid="main-app">
        <AuthWrapper
          firebase={this.props.firebase}
          signedInHandler={this.handleSignedIn}
          render={authWrapperState => {
            switch (this.state.isSignedIn) {
              case true:
                console.log('App.MainApp.render: signed-in state.');
                return <SignedInApp {...authWrapperState} />;
              case false:
                console.log('App.MainApp.render: signed-out state.');
                return <SignedOutApp firebase={this.props.firebase} />;
              default:
                console.log('App.MainApp.render: unknown sign-in state.');
                // We haven't figured out if we're signed in or not yet. Don't
                // display anything.
                return <div data-testid="unknown-app" />;
            }
          }}
        />
      </div>
    );
  }
}

/** Directs most routes to our main app, but some auth-less routes to shims. */
class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      firebase:
        props.firebase !== undefined ? props.firebase : new FirebaseState(),
    };
  }

  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Switch>
            <Route path="/services">
              <div>Misconfigured.</div>
            </Route>
            <Route path="/privacy">
              <Privacy />
            </Route>
            <Route path="/tos">
              <ToS />
            </Route>
            <Route>
              <MainApp firebase={this.state.firebase} />
            </Route>
          </Switch>
        </Router>
      </MuiThemeProvider>
    );
  }
}
export default App;

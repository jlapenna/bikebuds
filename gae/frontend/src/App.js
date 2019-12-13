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

import { createTheme } from './theme';

import { FirebaseState } from './firebase_util';

import AuthWrapper from './AuthWrapper';
import MainScreen from './MainScreen';
import Privacy from './Privacy';
import SpinnerScreen from './SpinnerScreen';
import SignInScreen from './SignInScreen';
import StandaloneSignup from './StandaloneSignup';
import ToS from './ToS';

class SignedInApp extends Component {
  static propTypes = {
    embed: PropTypes.bool.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
    firebaseToken: PropTypes.string.isRequired,
  };

  render() {
    return (
      <Router>
        <Switch>
          <Route
            path="/embed/"
            render={routeProps => (
              <MainScreen embed {...this.props} {...routeProps} />
            )}
          />
          <Route
            path="/signup"
            render={routeProps => (
              <StandaloneSignup {...this.props} {...routeProps} />
            )}
          />
          <Route
            path="/"
            render={routeProps => (
              <MainScreen embed={false} {...this.props} {...routeProps} />
            )}
          />
          <Route>
            <Redirect to="/" />
          </Route>
        </Switch>
      </Router>
    );
  }
}

export class SignedOutApp extends Component {
  static propTypes = {
    firebase: PropTypes.object.isRequired,
  };

  render() {
    return (
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
    );
  }
}

export class MainApp extends Component {
  static propTypes = {
    embed: PropTypes.bool.isRequired,
    firebase: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      loading: true,
    };
  }

  updateLoadingState = loadingUpdate => {
    this.setState({
      loading: loadingUpdate,
    });
  };

  render() {
    return (
      <AuthWrapper
        embed={this.props.embed}
        firebase={this.props.firebase}
        render={authWrapperState => {
          if (authWrapperState.isSignedIn() === undefined) {
            return (
              <SpinnerScreen>
                <span data-testid="unknown-app">Loading bikebuds...</span>
              </SpinnerScreen>
            );
          }
          if (this.props.embed) {
            if (authWrapperState.isSignedIn()) {
              return (
                <SignedInApp embed={this.props.embed} {...authWrapperState} />
              );
            } else {
              return (
                <SpinnerScreen>
                  <span data-testid="unknown-app">Loading bikebuds...</span>
                </SpinnerScreen>
              );
            }
          } else {
            if (authWrapperState.isSignedIn()) {
              return (
                <SignedInApp embed={this.props.embed} {...authWrapperState} />
              );
            } else {
              return (
                <SignedOutApp
                  embed={this.props.embed}
                  firebase={this.props.firebase}
                />
              );
            }
          }
        }}
      />
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
      colorType: 'dark',
    };
  }

  componentDidMount() {
    var colorType = new URLSearchParams(window.location.search).get(
      'colorType'
    );
    this.setState({ colorType: colorType ? colorType : 'dark' });
  }

  render() {
    var theme = createTheme(this.state.colorType);
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
            <Route path="/embed">
              <MainApp embed={true} firebase={this.state.firebase} />
            </Route>
            <Route>
              <MainApp embed={false} firebase={this.state.firebase} />
            </Route>
          </Switch>
        </Router>
      </MuiThemeProvider>
    );
  }
}
export default App;

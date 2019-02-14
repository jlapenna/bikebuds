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

import {
  Redirect,
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom';

import CssBaseline from '@material-ui/core/CssBaseline';

import { MuiThemeProvider } from '@material-ui/core/styles';
import theme from './theme';

import CookieConsent from 'react-cookie-consent';

import { firebaseState } from './firebase_util';
import Main from './Main';
import SignInScreen from './SignInScreen';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isSignedIn: undefined,
      firebaseUser: undefined
    };
  }

  /**
   * @inheritDoc
   */
  componentDidMount() {
    this.unregisterAuthObserver = firebaseState.auth.onAuthStateChanged(
      firebaseUser => {
        console.log('App.onAuthStateChanged: ', firebaseUser);
        // If we've unmounted before this callback executes, we don't want to
        // update state.
        if (this.unregisterAuthObserver === null) {
          return;
        }
        this.setState({
          isSignedIn: !!firebaseUser,
          firebaseUser: firebaseUser
        });
      }
    );
    this.unregisterAuthObserverNext = firebaseState.authNext.onAuthStateChanged(
      firebaseUser => {
        console.log('App.onAuthStateChanged: Next', firebaseUser);
        // If we've unmounted before this callback executes, we don't want to
        // update state.
        if (this.unregisterAuthObserverNext === null) {
          return;
        }
        this.setState({
          isSignedInNext: !!firebaseUser,
          firebaseUserNext: firebaseUser
        });
      }
    );
  }

  /**
   * @inheritDoc
   */
  componentWillUnmount() {
    this.unregisterAuthObserverNext();
    this.unregisterAuthObserverNext = null;
    this.unregisterAuthObserver();
    this.unregisterAuthObserver = null;
  }

  renderSignedInRouter() {
    return (
      <Router>
        <Switch>
          <Route path="/app">
            <Redirect to="/" />
          </Route>
          <Route path="/signin">
            <Redirect to="/" />
          </Route>
          <Route path="/services">
            <div>Misconfigured.</div>
          </Route>
          <Route>
            <Main
              firebaseState={firebaseState}
              firebaseUser={this.state.firebaseUser}
            />
          </Route>
        </Switch>
      </Router>
    );
  }

  renderSignedOutRouter() {
    return (
      <Router>
        <Switch>
          <Route path="/signin">
            <SignInScreen firebaseState={firebaseState} />
          </Route>
          <Route path="/services">
            <div>Misconfigured.</div>
          </Route>
          <Route path="/">
            <Redirect to="/signin" />
          </Route>
        </Switch>
      </Router>
    );
  }

  render() {
    if (this.state.isSignedIn === undefined) {
      // We haven't initialized state, so we don't know what to render.
      return null;
    }
    return (
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {this.state.isSignedIn
          ? this.renderSignedInRouter()
          : this.renderSignedOutRouter()}
        <CookieConsent buttonStyle={{ backgroundColor: '#03dac6' }}>
          This website uses cookies to enhance the user experience.
        </CookieConsent>
      </MuiThemeProvider>
    );
  }
}
export default App;

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

import 'typeface-roboto';

import theme from './theme';

import { config } from './config';

import { FirebaseState } from './firebase_util';

import Embed from './Embed';
import Main from './Main';
import Privacy from './Privacy';
import SignInScreen from './SignInScreen';
import StandaloneSignup from './StandaloneSignup';
import ToS from './ToS';

class MainApp extends Component {
  constructor(props) {
    super(props);
    this.state = {
      firebase:
        props.firebase !== undefined
          ? props.firebase
          : new FirebaseState(true /* enableMessaging */),
      isSignedIn: undefined,
      firebaseUser: undefined,
      isSignedInNext: undefined,
      firebaseUserNext: undefined
    };
  }

  _isSignedIn() {
    if (
      this.state.isSignedIn === undefined ||
      this.state.isSignedInNext === undefined
    ) {
      return undefined;
    }
    return this.state.isSignedIn && this.state.isSignedInNext;
  }

  componentDidMount() {
    if (config.isDev && config.fakeUser) {
      console.log('MainApp: Warning: Using Fake User.');
      const firebaseUser = {
        displayName: 'Fake User',
        photoUrl: '/logo-round.svg'
      };
      this.setState({
        isSignedIn: true,
        firebaseUser: firebaseUser,
        isSignedInNext: true,
        firebaseUserNext: firebaseUser
      });
      return;
    }

    console.log('MainApp: Using Real Auth');
    this.unregisterAuthObserver = this.state.firebase.onAuthStateChanged(
      firebaseUser => {
        console.log('MainApp.onAuthStateChanged: ', firebaseUser);
        // If we've unmounted before this callback executes, we don't want to
        // update state.
        if (this.unregisterAuthObserver === null) {
          return;
        }
        this.setState({
          isSignedIn: !!firebaseUser,
          firebaseUser: firebaseUser
        });
        firebaseUser.getIdTokenResult().then(idTokenResult => {
          firebaseUser.admin = !!idTokenResult.claims['admin'];
          this.setState({
            firebaseUser: firebaseUser
          });
        });
      },
      firebaseUser => {
        console.log('MainApp.onAuthStateChanged: Next', firebaseUser);
        // If we've unmounted before this callback executes, we don't want to
        // update state.
        if (this.unregisterAuthObserver === null) {
          return;
        }
        this.setState({
          isSignedInNext: !!firebaseUser,
          firebaseUserNext: firebaseUser
        });
        firebaseUser.getIdTokenResult().then(idTokenResult => {
          firebaseUser.admin = !!idTokenResult.claims['admin'];
          this.setState({
            firebaseUser: firebaseUser
          });
        });
      }
    );
  }

  componentWillUnmount() {
    if (!!this.unregisterAuthObserver) {
      this.unregisterAuthObserver();
      this.unregisterAuthObserver = null;
    }
  }

  renderSignedInRouter() {
    return (
      <Router>
        <Switch>
          <Route
            path="/signup"
            render={props => (
              <StandaloneSignup
                firebase={this.state.firebase}
                firebaseUser={
                  this._isSignedIn() ? this.state.firebaseUser : undefined
                }
                match={props.match}
              />
            )}
          />
          <Route
            path="/embed/"
            render={props => (
              <Embed
                firebase={this.state.firebase}
                firebaseUser={
                  this._isSignedIn() ? this.state.firebaseUser : undefined
                }
                match={props.match}
              />
            )}
          />
          <Route
            path="/"
            render={props => (
              <Main
                firebase={this.state.firebase}
                firebaseUser={
                  this._isSignedIn() ? this.state.firebaseUser : undefined
                }
                match={props.match}
              />
            )}
          />
          <Route path="">
            <Redirect to="/" />
          </Route>
        </Switch>
      </Router>
    );
  }

  renderSignedOutRouter() {
    return (
      <Router>
        <Switch>
          <Route
            path="/signin"
            render={props => (
              <SignInScreen
                firebase={this.state.firebase}
                firebaseUser={
                  this._isSignedIn() ? this.state.firebaseUser : undefined
                }
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

  render() {
    console.log('MainApp.render: ', this.state);
    if (this._isSignedIn() === undefined) {
      console.log('MainApp.render: Still uninitialized');
      // We haven't initialized state, so we don't know what to render.
      return null;
    }
    // I can't make this router nicer, as putting routes inside a fragment
    // as the fragments then contain the routes, which the switch doesn't know
    // how to properly switch with.
    return (
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {this._isSignedIn()
          ? this.renderSignedInRouter()
          : this.renderSignedOutRouter()}
      </MuiThemeProvider>
    );
  }
}

/** Directs most routes to our main app, but some auth-less routes to shims. */
class App extends Component {
  render() {
    console.log('App.render: ', this.state);
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
              <MainApp />
            </Route>
          </Switch>
        </Router>
      </MuiThemeProvider>
    );
  }
}
export default App;

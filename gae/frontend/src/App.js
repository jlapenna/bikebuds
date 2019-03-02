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

import { FirebaseState, FirebaseContext } from './firebase_util';

import Main from './Main';
import Privacy from './Privacy';
import SignInScreen from './SignInScreen';
import ToS from './ToS';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      firebase:
        props.firebase !== undefined ? props.firebase : new FirebaseState(),
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

  /**
   * @inheritDoc
   */
  componentDidMount() {
    this.unregisterAuthObserver = this.state.firebase.onAuthStateChanged(
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
      },
      firebaseUser => {
        console.log('App.onAuthStateChanged: Next', firebaseUser);
        // If we've unmounted before this callback executes, we don't want to
        // update state.
        if (this.unregisterAuthObserver === null) {
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
    this.unregisterAuthObserver();
    this.unregisterAuthObserver = null;
  }

  renderSignedInRouter() {
    return (
      <Router>
        <Switch>
          <Route path="/privacy">
            <Privacy />
          </Route>
          <Route path="/tos">
            <ToS />
          </Route>
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
              firebase={this.state.firebase}
              firebaseUser={
                this._isSignedIn() ? this.state.firebaseUser : undefined
              }
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
          <Route path="/privacy">
            <Privacy />
          </Route>
          <Route path="/tos">
            <ToS />
          </Route>
          <Route path="/signin">
            <SignInScreen firebase={this.state.firebase} />
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
    console.log('App.render: ', this.state);
    if (this._isSignedIn() === undefined) {
      console.log('App.render: Still uninitialized');
      // We haven't initialized state, so we don't know what to render.
      return null;
    }
    return (
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        <FirebaseContext.Provider value={this.state.firebase}>
          {this._isSignedIn()
            ? this.renderSignedInRouter()
            : this.renderSignedOutRouter()}
        </FirebaseContext.Provider>
      </MuiThemeProvider>
    );
  }
}
export default App;

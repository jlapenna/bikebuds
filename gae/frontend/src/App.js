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

import { Redirect, BrowserRouter as Router, Route, Switch,
    } from "react-router-dom";

import firebase from 'firebase/app';

import CssBaseline from '@material-ui/core/CssBaseline';

import { MuiThemeProvider } from '@material-ui/core/styles';
import theme from './theme';

import { config } from './Config';
import Main from './Main';
import SignInScreen from './SignInScreen';

firebase.initializeApp(config);


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isSignedIn: undefined,
      firebaseUser: undefined,
    };
  }

  /**
   * @inheritDoc
   */
  componentDidMount() {
    this.unregisterAuthObserver =
      firebase.auth().onAuthStateChanged((firebaseUser) => {
        this.setState({isSignedIn: !!firebaseUser, firebaseUser: firebaseUser});
      });
  };

  /**
   * @inheritDoc
   */
  componentWillUnmount() {
    this.unregisterAuthObserver();
  };

  render() {
    if (this.state.isSignedIn === undefined) {
      // We haven't initialized state, so we don't know what to render.
      return null;
    }
    if (this.state.isSignedIn) {
      return (
        <MuiThemeProvider theme={theme}>
          <CssBaseline />
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
                <Main firebaseUser={this.state.firebaseUser}/>
              </Route>
            </Switch>
          </Router>
        </MuiThemeProvider>
      );
    }

    // Not signed in.
    return (
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Switch>
            <Route path="/signin">
              <SignInScreen />
            </Route>
            <Route path="/services">
              <div>Misconfigured.</div>
            </Route>
            <Route path="/">
              <Redirect to="/signin" />
            </Route>
          </Switch>
        </Router>
      </MuiThemeProvider>
    );
  }
}
export default App;

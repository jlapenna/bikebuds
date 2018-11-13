import React, { Component } from 'react';

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
          <Main firebaseUser={this.state.firebaseUser}/>
        </MuiThemeProvider>
      );
    } else {
      return (
        <MuiThemeProvider theme={theme}>
          <CssBaseline />
          <SignInScreen />
        </MuiThemeProvider>
      );
    }
  };
}
export default App;

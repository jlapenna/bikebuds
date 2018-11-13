import React, { Component } from 'react';
import './App.css';

import firebase from 'firebase/app';

import CssBaseline from '@material-ui/core/CssBaseline';
import Grid from '@material-ui/core/Grid';

import { MuiThemeProvider } from '@material-ui/core/styles';
import theme from './theme';

import { config } from './Config';
import GapiWrapper from './GapiWrapper';
import SignInScreen from './Auth';

import ProfileCard from './ProfileCard';
import ServiceCard from './ServiceCard';

firebase.initializeApp(config);


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isSignedIn: undefined,
      firebaseUser: undefined,
      gapiReady: false,
    };
    this.onGapiReady = this.onGapiReady.bind(this);
  }

  onGapiReady() {
    this.setState({gapiReady: true});
    console.log('App: gapiReady');
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
          <React.Fragment>
            <CssBaseline />
            <Grid container className="App" spacing={16}
              style={{margin: 0, width: '100%'}}>
              <Grid item>
                <ProfileCard firebaseUser={this.state.firebaseUser}
                  gapiReady={this.state.gapiReady} />
              </Grid>
              <Grid item>
                <ServiceCard serviceName="strava"
                  gapiReady={this.state.gapiReady} />
              </Grid>
              <Grid item>
                <ServiceCard serviceName="withings"
                  gapiReady={this.state.gapiReady} />
              </Grid>
            </Grid>
            <GapiWrapper onReady={this.onGapiReady} />
          </React.Fragment>
        </MuiThemeProvider>
      );
    } else {
      return (
        <React.Fragment>
          <CssBaseline />
          <div className="App">
            <img src="icon.png" />
            <SignInScreen />
          </div>
        </React.Fragment>
      );
    }
  };
}
export default App;

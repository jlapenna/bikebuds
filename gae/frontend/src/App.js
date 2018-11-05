import React, { Component } from 'react';
import './App.css';

import firebase from 'firebase/app';

import CssBaseline from '@material-ui/core/CssBaseline';

import { MuiThemeProvider } from '@material-ui/core/styles';
import theme from './theme';
import { config } from './Config';
import GapiWrapper from './GapiWrapper';
import SignInScreen from './Auth';


firebase.initializeApp(config);


class App extends Component {
  constructor(props) {
    super(props);
    this.onGapiReady = this.onGapiReady.bind(this);
  }

  onGapiReady() {
    this.setState({gapiReady: true});
    console.log('App: gapiReady');
  }

  render() {
    return (
        <MuiThemeProvider theme={theme}>
          <React.Fragment>
            <CssBaseline />
            <div className="App">
              <SignInScreen />
              <GapiWrapper onReady={this.onGapiReady} />
            </div>
          </React.Fragment>
        </MuiThemeProvider>
    );
  };
}
export default App;

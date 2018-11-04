import React, { Component } from 'react';
import './App.css';

import firebase from 'firebase/app';

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
      <div className="App">
        <SignInScreen />
        <GapiWrapper onReady={this.onGapiReady} />
      </div>
    );
  };
}
export default App;

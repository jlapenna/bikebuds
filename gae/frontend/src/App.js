import React, { Component } from 'react';
import './App.css';

import firebase from 'firebase/app';

import { config } from './Config';
import GapiWrapper from './GapiWrapper';
import SignInScreen from './Auth';


firebase.initializeApp(config);


class App extends Component {

  render() {
    return (
      <div className="App">
        <SignInScreen />
        <GapiWrapper />
      </div>
    );
  };
}
export default App;

import React, { Component } from 'react';
import './App.css';

import firebase from 'firebase/app';
import 'firebase/auth';
import StyledFirebaseAuth from 'react-firebaseui/StyledFirebaseAuth';

import { backendConfig, config } from './Config';
import GapiWrapper from './GapiWrapper';


firebase.initializeApp(config);


class SignInScreen extends React.Component {
  constructor(props) {
    super(props);
    this.handleSignOut = this.handleSignOut.bind(this);
  };

  state = {
    isSignedIn: undefined,
  };

  uiConfig = {
    // Popup signin flow rather than redirect flow.
    callbacks: {
      signInSuccessWithAuthResult: function(authResult, redirectUrl) {
        console.log('signInsuccessWithAuthResult', authResult);
        // Return false to not redirect
        return false;
      },
    },
    signInFlow: 'popup',
    signInOptions: [
      {
        provider: firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        // Required to enable one-tap sign-up for YOLO
        //authMethod: 'https://accounts.google.com',
      },
    ],
    // Required to enable one-tap sign-up for YOLO
    //credentialHelper: firebaseui.auth.CredentialHelper.GOOGLE_YOLO
  };

  /**
   * @inheritDoc
   */
  componentDidMount() {
    this.unregisterAuthObserver = firebase.auth().onAuthStateChanged((user) => {
      var signedIn = !!user;
      console.log('SignInScreen: onAuthStateChanged', signedIn, user);
      this.setState({isSignedIn: signedIn});

      if (signedIn) {
        // Establish a cookie based session for this user for when we hit the
        // backend.
        user.getIdToken().then(this.createSession);
      }
    });
  };

  /**
   * @inheritDoc
   */
  componentWillUnmount() {
    console.log('SignInScreen: componentWillUnmount');
    this.unregisterAuthObserver();
  };

  handleSignOut(e) { 
    console.log('handleSignOut', e);
    firebase.auth().currentUser.getIdToken().then(function(idToken) {
      firebase.auth().signOut();
      fetch(backendConfig.backendHostUrl + '/close_session', {
        // Set header for the XMLHttpRequest to get data from the web server
        // associated with userIdToken
        headers: {
          'Authorization': 'Bearer ' + idToken
        },
        method: 'POST',
        credentials: 'include'
      }).then(function(data){
        // Ensure that we actually release the cookie we had cleared via
        // close_session
        window.location.reload();
        console.log("handleSignOut: complete", data);
      });
    });
  };

  createSession(idToken) {
    console.log('createSession');
    return fetch(backendConfig.backendHostUrl + '/create_session', {
      /* Set header for the XMLHttpRequest to get data from the web server
      associated with userIdToken */
      headers: {
        'Authorization': 'Bearer ' + idToken
      },
      method: 'POST',
      credentials: 'include'
    }).then(function(data){
      console.log("createSession: complete: ", data);
    });
  };

  render() {
    if (this.state.isSignedIn === undefined) {
      // We haven't initialized state, so we don't know what to render.
      return null;
    }
    if (this.state.isSignedIn) {
      return (
        <div>
          <p>Welcome {firebase.auth().currentUser.displayName}!</p>
          <button onClick={this.handleSignOut}>Sign-out</button>
        </div>
      );
    } else {
      return (
        <div>
          <h1>Bikebuds</h1>
          <StyledFirebaseAuth uiConfig={this.uiConfig} firebaseAuth={firebase.auth()}/>
        </div>
      );
    }
  };
}


class App extends Component {

  state = {
    isSignedIn: undefined,
  };

  /**
   * @inheritDoc
   */
  componentDidMount() {
    this.unregisterAuthObserver = firebase.auth().onAuthStateChanged((user) => {
      var signedIn = !!user;
      console.log('App: onAuthStateChanged', signedIn, user);
      this.setState({isSignedIn: signedIn});

      if (!signedIn) {
        return;
      }
      // Establish a cookie based session for this user for when we hit the
      // backend.
      user.getIdToken().then(this.createSession);
    });
  };

  /**
   * @inheritDoc
   */
  componentWillUnmount() {
    console.log('App: componentWillUnmount');
    this.unregisterAuthObserver();
  };

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

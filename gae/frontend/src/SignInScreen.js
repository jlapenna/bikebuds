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

import { withStyles } from '@material-ui/core/styles';

import firebase from 'firebase/app';
import 'firebase/auth';
import StyledFirebaseAuth from 'react-firebaseui/StyledFirebaseAuth';


const styles = {
  logo: {
    display: "block",
    margin : "20px auto 10px",
  },
}


class SignInScreen extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isSignedIn: undefined,
    };
    this.handleSignOut = this.handleSignOut.bind(this);
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
    });
  };

  render() {
    const { classes } = this.props;
    if (this.state.isSignedIn === undefined) {
      // We haven't initialized state, so we don't know what to render.
      return null;
    }
    if (this.state.isSignedIn) {
      return null;
    }
    return (
      <div>
        <img className={classes.logo} alt="bikebuds logo" src="icon.png" />
        <StyledFirebaseAuth uiConfig={this.uiConfig} firebaseAuth={firebase.auth()}/>
      </div>
    );
  };
}

export default withStyles(styles)(SignInScreen);

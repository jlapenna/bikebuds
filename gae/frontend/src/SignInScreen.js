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

import PropTypes from 'prop-types';
import React, { Component } from 'react';

import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

import firebase from 'firebase/app';
import 'firebase/auth';
import StyledFirebaseAuth from 'react-firebaseui/StyledFirebaseAuth';

import logoRound from './logo-round.svg';

class SignInScreen extends Component {
  static styles = {
    logo: {
      display: 'block',
      margin: '20px auto 10px'
    },
    privacyFooter: {
      'text-align': 'center'
    }
  };

  static propTypes = {
    firebase: PropTypes.object.isRequired
  };

  handleSignInSuccessWithAuthResult = (authResult, redirectUrl) => {
    console.log('SignInScreen.signInSuccessWithAuthResult', authResult);
    this.props.firebase.authNext
      .signInAndRetrieveDataWithCredential(authResult.credential)
      .then(signInResult => {
        console.log(
          'SignInScreen.signInWithCredential: result:',
          authResult,
          signInResult
        );
      })
      .catch(error => {
        console.log(
          'SignInScreen.signInWithCredential: catch:',
          authResult,
          error
        );
      });
    console.log(
      'SignInScreen.signInSuccessWithAuthResult: Started NEXT sign in'
    );

    // Return false to not redirect
    return false;
  };

  uiConfig = {
    // Popup signin flow rather than redirect flow.
    callbacks: {
      signInSuccessWithAuthResult: this.handleSignInSuccessWithAuthResult
    },
    signInFlow: 'popup',
    signInOptions: [
      {
        provider: firebase.auth.GoogleAuthProvider.PROVIDER_ID
        // Required to enable one-tap sign-up for YOLO
        //authMethod: 'https://accounts.google.com',
      }
    ]
    // Required to enable one-tap sign-up for YOLO
    //credentialHelper: firebaseui.auth.CredentialHelper.GOOGLE_YOLO
  };

  render() {
    const { classes } = this.props;
    return (
      <div>
        <img className={classes.logo} alt="Bikebuds Logo" src={logoRound} />
        <StyledFirebaseAuth
          uiConfig={this.uiConfig}
          firebaseAuth={this.props.firebase.auth}
        />
        <Typography
          className={this.props.classes.privacyFooter}
          variant="caption"
        >
          <a href="/privacy">Privacy</a> - <a href="/tos">ToS</a>
        </Typography>
      </div>
    );
  }
}
export default withStyles(SignInScreen.styles)(SignInScreen);

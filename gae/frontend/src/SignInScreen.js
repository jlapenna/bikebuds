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

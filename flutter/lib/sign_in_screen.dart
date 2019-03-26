// Copyright 2019 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/privacy_util.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';

final GoogleSignIn googleSignIn = GoogleSignIn();

class SignInScreen extends StatefulWidget {
  @override
  _SignInScreenState createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  var signingIn = false;

  doSignIn() async {
    print('SignInScreen.doSignIn: $widget.firebase');
    setState(() {
      this.signingIn = true;
    });

    // Otherwise, try to find the user's Google Identity.
    var googleUser = googleSignIn.currentUser;
    if (googleUser == null) {
      print('SignInScreen.doSignIn: signInSilently');
      googleUser = await googleSignIn.signInSilently();
    }
    if (googleUser == null) {
      print('SignInScreen.doSignIn: signIn');
      googleUser = await googleSignIn.signIn();
    }
    print('SignInScreen.doSignIn: googleUser.authenticate: ${googleUser?.id}');

    if (googleUser == null) {
      // The user aborted Google sign in.
      Navigator.pop(context, null);
      return;
    }

    // Get auth credentials to sign into firebase.
    var googleAuth = await googleUser.authentication;
    final AuthCredential credential = GoogleAuthProvider.getCredential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );

    var firebase = FirebaseContainer.of(context);

    // Sign in with the "next" firebase project.
    print('SignInScreen.doSignIn: next: signInWithCredential');
    var firebaseNextUser =
        await firebase.authNext.signInWithCredential(credential);
    await firebaseNextUser.getIdToken(refresh: true);

    // Sign into the primary project.
    print('SignInScreen.doSignIn: signInWithCredential');
    var firebaseUser = await firebase.auth.signInWithCredential(credential);
    await firebaseUser.getIdToken(refresh: true);

    var state = FirebaseSignInState(firebaseUser, firebaseNextUser);

    print('SignInScreen.doSignIn: Popping from: $state');
    Navigator.pop(context, state);
  }

  Widget buildSigningIn(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        Column(
          children: <Widget>[
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                CircularProgressIndicator(),
                SizedBox(width: 20.0),
              ],
            ),
          ],
        ),
      ],
    );
  }

  Widget buildStartSignIn(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.max,
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Image.asset("assets/logo-round.png"),
          RaisedButton(
            color: Colors.white,
            child: Text("Sign in with Google"),
            onPressed: () => doSignIn(),
          ),
          FlatButton(
            child: Text("Privacy - ToS"),
            onPressed: () {
              showPrivacyDialog(context);
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    print('SignInScreen.build');
    return Scaffold(
      body: signingIn ? buildSigningIn(context) : buildStartSignIn(context),
    );
  }
}

Future<FirebaseSignInState> ensureSignedIn(
    BuildContext context, firebase) async {
  var firebaseUserFuture = firebase.auth.currentUser();
  var firebaseNextUserFuture = firebase.authNext.currentUser();
  FirebaseSignInState signInState = FirebaseSignInState(
      await firebaseUserFuture, await firebaseNextUserFuture);
  print('ensureSignedIn: signedIn: ${signInState.signedIn}');

  // If we already have the right users, we don't have to sign in. Sweet!
  if (signInState.signedIn) {
    return signInState;
  }

  // Otherwise launch the sign in screen and wait for a result.
  print('ensureSignedIn: awaiting SignInScreen');
  return Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => SignInScreen(),
    ),
  );
}

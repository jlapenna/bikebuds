/**
 * Copyright 2019 Google Inc. All Rights Reserved.
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

import 'package:bikebuds/firebase_util.dart';
//import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';

class SignInScreen extends StatefulWidget {
  final GoogleSignIn googleSignIn;
  final FirebaseState firebase;
  final FirebaseState firebaseNext;
  final dynamic onSignInComplete;

  SignInScreen(this.googleSignIn, this.firebase, this.firebaseNext,
      this.onSignInComplete,
      {Key key})
      : super(key: key);

  @override
  _SignInScreenState createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  GoogleSignInAuthentication googleAuth;
  bool firebaseGoogleSignInStarted = false;

  @override
  void initState() {
    super.initState();
    print('SplashScreen.initState: ${widget.firebase}, ${widget.firebaseNext}');
    if (widget.firebase?.auth == null || widget.firebaseNext?.auth == null) {
      print('SplashScreen.initState: Not ready to sign in, waiting for next.');
      return;
    }

    _startSignIn();
  }

  void _startSignIn() async {
    print('SplashScreen._startSignIn');
    await _doSignIn();
    Navigator.pushReplacementNamed(context, "/home");
    widget.onSignInComplete(await widget.firebase.auth.currentUser());
  }

  Future _doSignIn() async {
    print('SplashScreen._doSignIn: ${widget.firebase}, ${widget.firebaseNext}');

    // If we already have the right users, we don't have to sign in. Sweet!
    var firebaseUserFuture = widget.firebase.auth.currentUser();
    var firebaseNextUserFuture = widget.firebaseNext.auth.currentUser();
    if (firebaseUserFuture != null && firebaseNextUserFuture != null) {
      return Future.wait([firebaseUserFuture, firebaseNextUserFuture]);
    }

    // Otherwise, try to find the user's Google Identity.
    var googleUser = widget.googleSignIn.currentUser;
    if (googleUser == null) {
      print('SplashScreen._doSignIn: signInSilently');
      googleUser = await widget.googleSignIn.signInSilently();
    }
    if (googleUser == null) {
      print('SplashScreen._doSignIn: signIn');
      googleUser = await widget.googleSignIn.signIn();
    }
    print('SplashScreen._doSignIn: googleUser.authenticate');
    googleAuth = await googleUser.authentication;
//    final AuthCredential credential = GoogleAuthProvider.getCredential(
//      accessToken: googleAuth.accessToken,
//      idToken: googleAuth.idToken,
//    );

    // Then authenticate the google identity with firebase to get a firebase user.
    print('SplashScreen._doSignIn: signInWithGoogle');
    firebaseUserFuture = widget.firebase.auth.currentUser();
    if (firebaseUserFuture == null) {
//      firebaseUserFuture =
//          widget.firebase.auth.signInWithCredential(credential);
//      firebaseUserFuture =
      widget.firebase.auth.signInWithGoogle(
          idToken: googleAuth.idToken, accessToken: googleAuth.accessToken);
    }

    // Then do that with the other firebase project.
    print('SplashScreen._doSignIn: next: signInWithGoogle');
//    firebaseNextUserFuture =
//        widget.firebaseNext.auth.signInWithCredential(credential);
    widget.firebaseNext.auth.signInWithGoogle(
        idToken: googleAuth.idToken, accessToken: googleAuth.accessToken);

    return Future.wait([firebaseUserFuture, firebaseNextUserFuture]);
  }

  @override
  Widget build(BuildContext context) {
    return buildSignInProgressScaffold();
  }
}

Scaffold buildSignInProgressScaffold() {
  return new Scaffold(
    body: new Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        new Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            new CircularProgressIndicator(),
            new SizedBox(width: 20.0),
            new Text("Signing in..."),
          ],
        ),
      ],
    ),
  );
}

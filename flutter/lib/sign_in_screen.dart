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
import 'package:flutter/widgets.dart';
import 'package:google_sign_in/google_sign_in.dart';

class SignInContainer extends StatefulWidget {
  final Widget child;

  SignInContainer({@required this.child});

  static SignInContainerState of(BuildContext context) {
    return (context.inheritFromWidgetOfExactType(_InheritedSignIn)
            as _InheritedSignIn)
        .data;
  }

  @override
  SignInContainerState createState() => new SignInContainerState();
}

class SignInContainerState extends State<SignInContainer> {
  final GoogleSignIn googleSignIn = GoogleSignIn();

  // null means we haven't gotten our dependencies, yet.
  // A value means we've determined if the user is signed in at all.
  // The value inside determines sign in state.
  FirebaseSignInState signInState;

  // Determines if we've actively initialized a sign-in flow.
  bool signingIn = false;

  @override
  void didChangeDependencies() {
    var firebase = FirebaseContainer.of(context);
    if (firebase != null &&
        firebase.auth != null &&
        firebase.authNext != null) {
      _setInitialState(context, firebase);
    }
    super.didChangeDependencies();
  }

  _setInitialState(BuildContext context, firebase) async {
    print('SignInScreen._setInitialState');
    var firebaseUserFuture = firebase.auth.currentUser();
    var firebaseNextUserFuture = firebase.authNext.currentUser();
    FirebaseSignInState signInState = FirebaseSignInState(
        await firebaseUserFuture, await firebaseNextUserFuture);
    setState(() {
      print('SignInScreen._setInitialState: $signInState');
      this.signInState = signInState;
    });
  }

  _doSignIn() async {
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
      setState(() {
        this.signingIn = false;
        this.signInState = null;
      });
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

    setState(() {
      this.signingIn = false;
      this.signInState = FirebaseSignInState(firebaseUser, firebaseNextUser);
    });
  }

  @override
  Widget build(BuildContext context) {
    print('SignInContainerState.build');
    if (signInState == null) {
      // We do not have our dependencies, so we have not looked up
      // user state, yet.
      return new Container(width: 0.0, height: 0.0, color: Colors.white);
    }
    if (!signInState.signedIn) {
      // We have determined initial sign-in state, we're not signed in.
      // We might be in the process of signing in, though...
      return MaterialApp(
        home: Scaffold(
          body:
              signingIn ? _buildSigningIn(context) : _buildStartSignIn(context),
        ),
      );
    }
    return new _InheritedSignIn(
      data: this,
      child: widget.child,
    );
  }

  Widget _buildSigningIn(BuildContext context) {
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

  Widget _buildStartSignIn(BuildContext context) {
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
            onPressed: () => _doSignIn(),
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
}

class _InheritedSignIn extends InheritedWidget {
  // Data is your entire state. In our case just 'User'
  final SignInContainerState data;

  // You must pass through a child and your state.
  const _InheritedSignIn({
    Key key,
    @required this.data,
    @required Widget child,
  }) : super(key: key, child: child);

  // This is a built in method which you can use to check if
  // any state has changed. If not, no reason to rebuild all the widgets
  // that rely on your state.
  @override
  bool updateShouldNotify(_InheritedSignIn old) => true;
}

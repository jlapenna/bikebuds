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
import 'package:bikebuds/widgets/loading.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

class SignInScreen extends StatefulWidget {
  final WidgetBuilder signedInBuilder;

  SignInScreen({@required this.signedInBuilder});

  SignInScreenState createState() => new SignInScreenState();
}

class SignInScreenState extends State<SignInScreen> {
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  // Determines if we've actively initialized a sign-in flow.
  bool _signingIn = false;

  _doSignIn() async {
    setState(() {
      this._signingIn = true;
    });

    // Otherwise, try to find the user's Google Identity.
    var googleUser = _googleSignIn.currentUser;
    if (googleUser == null) {
      googleUser = await _googleSignIn.signInSilently();
    }
    if (googleUser == null) {
      googleUser = await _googleSignIn.signIn();
    }

    if (googleUser == null) {
      // The user aborted Google sign in.
      setState(() {
        this._signingIn = false;
        Provider.of<FirebaseSignInState>(context).update(null, null);
      });
      return;
    }

    // Get auth credentials to sign into firebase.
    var googleAuth = await googleUser.authentication;
    final AuthCredential credential = GoogleAuthProvider.getCredential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );

    var firebase = Provider.of<FirebaseState>(context);

    // Sign into the primary project.
    var authResult = await firebase.auth.signInWithCredential(credential);

    // Sign in with the "next" firebase project.
    var authResultNext =
        await firebase.authNext.signInWithCredential(credential);

    // Refresh ID Tokens, triggering an auth-state change.
    await authResult.user.getIdToken(refresh: true);
    await authResultNext.user.getIdToken(refresh: true);

    Provider.of<FirebaseSignInState>(context)
        .update(authResult.user, authResultNext.user);

    setState(() {
      this._signingIn = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    var signInState = Provider.of<FirebaseSignInState>(context);
    if (!signInState.isInitialized) {
      return new Container(width: 0.0, height: 0.0, color: Colors.white);
    }
    if (!signInState.signedIn) {
      // We have determined initial sign-in state, we're not signed in.
      // We might be in the process of signing in, though...
      return MaterialApp(
        home: Scaffold(
          body: _signingIn ? const Loading() : _buildStartSignIn(context),
        ),
      );
    } else {
      return widget.signedInBuilder(context);
    }
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
              showAboutDialog(context: context, children: <Widget>[
                ListTile(
                  title: Text("Terms of Service"),
                  onTap: () {
                    launch("https://bikebuds.com/tos");
                    Navigator.pop(context);
                  },
                ),
                ListTile(
                  title: Text("Privacy Policy"),
                  onTap: () {
                    launch("https://bikebuds.com/privacy");
                    Navigator.pop(context);
                  },
                ),
              ]);
            },
          ),
        ],
      ),
    );
  }
}

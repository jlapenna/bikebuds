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
  SignInScreen();

  SignInScreenState createState() => new SignInScreenState();
}

class SignInScreenState extends State<SignInScreen> {
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  // Determines if we've actively initialized a sign-in flow.
  bool _signingIn = false;

  Future _asyncSignIn() async {
    print('SignInScreen: _asyncSignIn');
    setState(() {
      this._signingIn = true;
    });

    var firebaseState = Provider.of<FirebaseState>(context, listen: false);
    var googleUser = _googleSignIn.currentUser;
    print('SignInScreen: Current user: ${googleUser?.id}');
    assert(googleUser == null || googleUser.id != null,
        "$googleUser should not have a null id");

    // Try silent sign in.
    if (googleUser?.id == null) {
      print('SignInScreen: Awaiting signInSilently');
      googleUser = await _googleSignIn.signInSilently();
    }
    print('SignInScreen: Finished silent signin attempt. ${googleUser?.id}');
    assert(googleUser == null || googleUser.id != null,
        "$googleUser should not have a null id");

    // Try manual sign in.
    if (googleUser?.id == null) {
      print('SignInScreen: Awaiting signIn');
      googleUser = await _googleSignIn.signIn();
    }
    print('SignInScreen: Current user: ${googleUser?.id}');
    assert(googleUser == null || googleUser.id != null,
        "$googleUser should not have a null id");

    // If we couldn't sign in, abort sign in.
    if (googleUser?.id == null) {
      print('SignInScreen: User aborted signIn.');
      setState(() {
        this._signingIn = false;
        firebaseState.signOut();
      });
      return;
    }

    // Get auth credentials to sign into firebase.
    print('SignInScreen: Awaiting authentication for ${googleUser.id}');
    var googleAuth = await googleUser.authentication;
    print('SignInScreen: Building credentials');
    final AuthCredential credential = GoogleAuthProvider.getCredential(
      idToken: googleAuth.idToken,
      accessToken: googleAuth.accessToken,
    );

    // Sign in with the "app" firebase project.
    print('SignInScreen: Awaiting SignInWithCredential');
    var authResult = await firebaseState.signInWithCredential(credential);

    // Sign in with the "next" firebase project.
    print('SignInScreen: Awaiting Next SignInWithCredential');
    var authResultNext =
        await firebaseState.signInWithCredentialNext(credential);

    // Refresh ID Tokens, triggering an auth-state change.
    print('SignInScreen: Awaiting Tokens');
    await authResult.user.getIdToken();
    await authResultNext.user.getIdToken();

    print('SignInScreen: Finished Sign-in');
    setState(() {
      this._signingIn = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return (_signingIn)
        ? const Loading(message: "Signing in...")
        : _buildStartSignIn(context);
  }

  Widget _buildStartSignIn(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.max,
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Expanded(
            flex: 1,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                Image.asset("assets/logo-round.png"),
                RaisedButton(
                    color: Colors.white,
                    child: Text("Sign in with Google"),
                    onPressed: () => _asyncSignIn().catchError((err) {
                          print('SignInScreen: Failed to _asyncSignIn: $err');
                        })),
              ],
            ),
          ),
          Expanded(
            flex: 0,
            child: FlatButton(
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
          ),
        ],
      ),
    );
  }
}

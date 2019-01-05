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

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

class SplashScreen extends StatefulWidget {
  final auth;
  final googleSignIn;

  SplashScreen(this.auth, this.googleSignIn, {Key key, this.title})
      : super(key: key);

  final String title;

  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    print("Initing");

    widget.auth.onAuthStateChanged
        .firstWhere((user) => user != null)
        .then((FirebaseUser user) async {
      print("Navigating");
      Navigator.pushReplacementNamed(context, "/home");
    });
    _signIn();
  }

  void _signIn() async {
    try {
      var googleUser = widget.googleSignIn.currentUser;
      if (googleUser == null) {
        googleUser = await widget.googleSignIn.signInSilently();
      }
      if (googleUser == null) {
        googleUser = await widget.googleSignIn.signIn();
      }
      var googleAuth = await googleUser.authentication;
      await widget.auth.signInWithGoogle(
          idToken: googleAuth.idToken, accessToken: googleAuth.accessToken);
      print("Completed signing in.");
    } catch (e) {
      print("Failed signing in.");
    }
  }

  @override
  Widget build(BuildContext context) {
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
}

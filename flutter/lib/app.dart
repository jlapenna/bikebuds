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

import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds/config.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/main_screen.dart';
import 'package:flutter/material.dart';

void main() => runApp(App());

const Color PRIMARY_COLOR = Color(0xFF03dac6);
const Color ACCENT_COLOR = Color(0xFFff4081);

class App extends StatefulWidget {
  @override
  _AppState createState() => _AppState();
}

class _AppState extends State<App> {
  FirebaseState firebase;
  BikebudsState bikebuds;
  Future<Map<String, dynamic>> config;

  @override
  void initState() {
    super.initState();
    config = loadConfig();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bikebuds',
      theme: ThemeData(
        primaryColor: PRIMARY_COLOR,
        accentColor: ACCENT_COLOR,
        buttonColor: PRIMARY_COLOR,
      ),
      initialRoute: '/',
      routes: <String, WidgetBuilder>{
        '/': (BuildContext context) =>
            MainScreen(config: config, onSignedIn: _handleSignedIn),
      },
    );
  }

  _handleSignedIn(FirebaseState firebase, BikebudsState bikebuds,
      FirebaseSignInState signedInState) {
    print('App._handleSignedIn: $firebase $signedInState');
    this.firebase = firebase;
    this.bikebuds = bikebuds;

    bikebuds.registerClient();
    firebase.registerMessaging();
  }
}

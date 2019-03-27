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
import 'package:bikebuds/sign_in_screen.dart';
import 'package:flutter/material.dart';

void main() => runApp(App());

const Color PRIMARY_COLOR = Color(0xFF03dac6);
const Color ACCENT_COLOR = Color(0xFFff4081);

class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ConfigContainer(
      child: FirebaseContainer(
        child: SignInContainer(
          child: BikebudsApiContainer(
            child: SignedInApp(),
          ),
        ),
      ),
    );
  }
}

class SignedInApp extends StatefulWidget {
  @override
  _SignedInAppState createState() => _SignedInAppState();
}

class _SignedInAppState extends State<SignedInApp> {
  @override
  void didChangeDependencies() {
    var bikebuds = BikebudsApiContainer.of(context);
    if (bikebuds.api != null) {
      var firebase = FirebaseContainer.of(context);
      print('Messaging.didDependenciesChange: configuring messaging');
      firebase.messaging.configure(
        onMessage: (Map<String, dynamic> message) async {
          print('on message $message');
        },
        onResume: (Map<String, dynamic> message) async {
          print('on resume $message');
        },
        onLaunch: (Map<String, dynamic> message) async {
          print('on launch $message');
        },
      );
      bikebuds.registerClient();
    }
    super.didChangeDependencies();
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
        '/': (BuildContext context) => MainScreen(),
      },
    );
  }
}

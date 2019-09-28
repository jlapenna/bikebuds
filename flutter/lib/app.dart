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

import 'dart:async';

import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds/config.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/loading.dart';
import 'package:bikebuds/main_screen.dart';
import 'package:bikebuds/sign_in_screen.dart';
import 'package:bikebuds/user_model.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:scoped_model/scoped_model.dart';

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
  final UserModel user = UserModel();

  StreamSubscription<FirebaseUser> _firebaseUserSubscription;
  StreamSubscription<String> _messagingListener;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    // Listen for auth changes.
    var bikebuds = BikebudsApiContainer.of(context);
    var firebase = FirebaseContainer.of(context);
    if (bikebuds.isReady() && this._firebaseUserSubscription == null) {
      this._firebaseUserSubscription =
          firebase.auth.onAuthStateChanged.listen((FirebaseUser firebaseUser) {
        user.updateFirebaseUser(firebaseUser);
        user.updateProfile(bikebuds.profile);
        user.updateAuth(bikebuds.auth);
      });
    }

    // Register FCM.
    if (bikebuds.isReady() && _messagingListener == null) {
      _messagingListener = firebase.messaging.onTokenRefresh.listen((token) {
        BikebudsApiContainer.of(context).registerClient(token).then((response) {
          print('App.Messaging: bikebuds.registerClient: complete');
        });
      });
      firebase.messaging.requestNotificationPermissions();
      firebase.messaging.configure(
          onMessage: this.onMessage,
          onResume: this.onResume,
          onLaunch: this.onLaunch);
    }
  }

  @override
  void dispose() {
    if (_firebaseUserSubscription != null) {
      _firebaseUserSubscription.cancel();
    }
    if (_messagingListener != null) {
      _messagingListener.cancel();
    }
    super.dispose();
  }

  Future<dynamic> onMessage(Map<String, dynamic> message) async {
    print('Messaging.onMessage: $message');
  }

  Future<dynamic> onResume(Map<String, dynamic> message) async {
    print('Messaging.onResume: $message');
  }

  Future<dynamic> onLaunch(Map<String, dynamic> message) async {
    print('Messaging.onLaunch: $message');
  }

  @override
  Widget build(BuildContext context) {
    return ScopedModel<UserModel>(
      model: user,
      child: ScopedModelDescendant<UserModel>(
          builder: (context, child, model) => buildApp(context)),
    );
  }

  Widget buildApp(BuildContext context) {
    // TODO: Check the profile here, look for signup_complete and block
    // full-app rendering if we aren't signed up.
    //User user = UserModel.of(context)?.bikebudsUser;

    var bikebuds = BikebudsApiContainer.of(context);
    if (!bikebuds.isReady()) {
      return loadingWidget(context);
    }
    return MaterialApp(
      title: 'Bikebuds',
      theme: ThemeData(
        primaryColor: PRIMARY_COLOR,
        accentColor: ACCENT_COLOR,
        buttonColor: PRIMARY_COLOR,
      ),
      initialRoute: '/',
      routes: <String, WidgetBuilder>{
        '/': (BuildContext context) {
          return MainScreen();
        },
      },
    );
  }
}

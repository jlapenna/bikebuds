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

import 'package:bikebuds/bikebuds_api_state.dart';
import 'package:bikebuds/config.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/main_screen.dart';
import 'package:bikebuds/sign_in_screen.dart';
import 'package:bikebuds/user_state.dart';
import 'package:bikebuds/widgets/loading.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

void main() => runApp(App());

const Color PRIMARY_COLOR = Color(0xFF03dac6);
const Color ACCENT_COLOR = Color(0xFFff4081);

class App extends StatefulWidget {
  @override
  _AppState createState() => _AppState();
}

class _AppState extends State<App> {
  var _loader;

  @override
  void initState() {
    _loader = loadConfig(context);
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Config>(
        future: _loader,
        builder: (context, AsyncSnapshot<Config> snapshot) {
          if (!snapshot.hasData) {
            return Container();
          }
          return MultiProvider(providers: [
            Provider<Config>.value(value: snapshot.data),
            ChangeNotifierProvider<FirebaseState>(
                create: (_) => FirebaseState(context)),
            ChangeNotifierProxyProvider<FirebaseState, UserState>(
                create: (_) => UserState(),
                update: (_, firebaseState, userState) =>
                    userState..firebaseUser = firebaseState.user),
            ChangeNotifierProxyProvider2<Config, FirebaseState,
                    BikebudsApiState>(
                create: (_) => BikebudsApiState(),
                update: (_, config, firebaseState, bikebudsApiState) =>
                    bikebudsApiState
                      ..config = config
                      ..firebaseState = firebaseState),
          ], child: AppDelegate());
        });
  }
}

class AppDelegate extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    var firebaseState = Provider.of<FirebaseState>(context);
    print('AppDelegate: build: initialized: ${firebaseState.authInitialized},' +
        'signedIn: ${firebaseState.signedIn}');
    return firebaseState.signedIn
        ? SignedInApp()
        : firebaseState.authInitialized ? SignedOutApp() : Container();
  }
}

class SignedOutApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'Bikebuds',
        theme: ThemeData.light().copyWith(
          primaryColor: PRIMARY_COLOR,
          accentColor: ACCENT_COLOR,
          buttonColor: PRIMARY_COLOR,
        ),
        darkTheme: ThemeData.dark().copyWith(
          primaryColor: PRIMARY_COLOR,
          accentColor: ACCENT_COLOR,
          buttonColor: PRIMARY_COLOR,
        ),
        home: Scaffold(body: SignInScreen()));
  }
}

class SignedInApp extends StatefulWidget {
  @override
  _SignedInAppState createState() => _SignedInAppState();
}

class _SignedInAppState extends State<SignedInApp> {
  bool _bikebudsFetched = false;
  StreamSubscription<FirebaseUser> _firebaseUserSubscription;
  StreamSubscription<String> _messagingListener;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    // Listen for auth changes.
    var firebase = Provider.of<FirebaseState>(context);
    var bikebuds = Provider.of<BikebudsApiState>(context);

    // TODO: Turn this into a stream.
    if (bikebuds.isReady && this._bikebudsFetched) {
      this._bikebudsFetched = true;
      bikebuds.profile.then((profile) {
        Provider.of<UserState>(context)..profile = profile;
      }).catchError((err) {
        print('$this: Failed to fetch profile: $err');
      });
    }

    // Register FCM.
    if (!kIsWeb && bikebuds.isReady && _messagingListener == null) {
      _messagingListener = firebase.messaging.onTokenRefresh.listen((token) {
        bikebuds.registerClient(token).then((response) {
          print('SignedInApp: bikebuds.registerClient: Complete');
        }).catchError((err) {
          print('SignedInApp: bikebuds.registerClient: Failed: $err');
        });
      });
      firebase.messaging.requestNotificationPermissions();
      firebase.messaging.configure(
          onMessage: this.onMessage,
          onResume: this.onResume,
          onLaunch: this.onLaunch);
    }

    // TODO: Check the profile here, look for signup_complete and block
    // full-app rendering if we aren't signed up.
    //User user = UserModel.of(context)?.bikebudsUser;
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
    var bikebuds = Provider.of<BikebudsApiState>(context);
    return MaterialApp(
      title: 'Bikebuds',
      theme: ThemeData.light().copyWith(
        primaryColor: PRIMARY_COLOR,
        accentColor: ACCENT_COLOR,
        buttonColor: PRIMARY_COLOR,
      ),
      darkTheme: ThemeData.dark().copyWith(
        primaryColor: PRIMARY_COLOR,
        accentColor: ACCENT_COLOR,
        buttonColor: PRIMARY_COLOR,
      ),
      initialRoute: '/',
      routes: <String, WidgetBuilder>{
        '/': (BuildContext context) {
          return bikebuds.isReady
              ? MainScreen()
              : Loading(message: "Loading bikebuds...");
        },
      },
    );
  }
}

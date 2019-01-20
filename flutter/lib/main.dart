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

import 'dart:async';

import 'package:bikebuds/firebase_container.dart';
import 'package:bikebuds/firebase_http_client.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/home_screen.dart';
import 'package:bikebuds/sign_in_screen.dart';
import 'package:bikebuds_api/bikebuds/v1.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:googleapis_auth/auth_io.dart';

void main() => runApp(App());

class App extends StatefulWidget {
  @override
  _AppState createState() => _AppState();
}

class _AppState extends State<App> {
  final GoogleSignIn googleSignIn = GoogleSignIn();
  final FirebaseState firebase = loadDefaultFirebase();

  Future<FirebaseState> firebaseNextLoader;

  StreamSubscription<FirebaseUser> _userListener;

  BikebudsApi _api;
  MainProfileResponse _profile;
  SharedDatastoreUsersClientMessage _client;

  @override
  void initState() {
    super.initState();

    // Services off the main project.
    firebaseNextLoader = loadNextFirebase(context);

    // Listen for future auth state changes.
    _userListener =
        firebase.auth.onAuthStateChanged.listen(_onAuthStateChanged);
  }

  void _onAuthStateChanged(user) async {
    print("_AppState._onAuthStateChanged: $user");
    if (user == null) {
      _api = null;
      setState(() {
        _profile = null;
      });
      return;
    }
    _api = await _loadBikebudsApi(user);

    var profileFuture = _api.getProfile(MainRequest());
    var clientFuture = _registerWithBikebuds();
    var profile = await profileFuture;
    var client = (await clientFuture)?.client;
    setState(() {
      _profile = profile;
      _client = client;
    });
  }

  Future<BikebudsApi> _loadBikebudsApi(user) async {
    print('_AppState._loadBikebudsApi');
    var token = await user.getIdToken(refresh: true);
    var options = await firebase.app.options;
    String key = options.apiKey;

    var api = BikebudsApi(FirebaseHttpClient(token, clientViaApiKey(key)));
    return api;
  }

  Future<MainClientResponse> _registerWithBikebuds() async {
    print('_AppState._registerWithBikebuds');
    var messagingToken = await firebase.messaging.getToken();
    var request = MainUpdateClientRequest()
      ..client = (SharedDatastoreUsersClientMessage()..id = messagingToken);
    return _api.updateClient(request);
  }

  @override
  void dispose() {
    _userListener?.cancel();
    super.dispose();
  }

  _handleSignInComplete(FirebaseUser user) {
    print('_AppState.handleSignInComplete: $user');
    if (user == null) {
      print('_AppState.handleSignInComplete: Unable to sign-in.');
      return;
    }

    // Now, register messaging on the default project.
    print('App._handleSignInComplete: requestNotificationPermission');
    firebase.messaging.requestNotificationPermissions();
    firebase.registerMessaging();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bikebuds',
      theme: ThemeData(
        primaryColor: Color(0xFF03dac6),
        accentColor: Color(0xFFff4081),
      ),
      initialRoute: '/',
      routes: buildRoutes());
  }

  Map<String, WidgetBuilder> buildRoutes() {
    print('_AppState.buildRoutes');
    return {
      '/': (context) => FutureBuilder(
          future: firebaseNextLoader,
          builder: (context, snapshot) {
            if (snapshot.hasData) {
              print('_AppState.build: hasData');
              var firebaseNext = snapshot.data;
              return SignInScreen(
                  googleSignIn, firebase, firebaseNext, _handleSignInComplete);
            } else {
              print('_AppState.build: noData');
              return buildSignInProgressScaffold();
            }
          }),
      '/home': (context) => FutureBuilder(
          future: firebaseNextLoader,
          builder: (context, snapshot) {
            if (snapshot.hasData) {
              print('_AppState.build: hasData');
              var firebaseNext = snapshot.data;
              return HomeScreen(
                  firebase: firebase,
                  firebaseNext: firebaseNext,
                  api: _api,
                  client: _client,
                  profile: _profile);
            } else {
              print('_AppState.build: noData');
              return buildSignInProgressScaffold();
            }
          }),
    };
  }
}

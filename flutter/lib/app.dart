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
import 'dart:isolate';

import 'package:bikebuds/bikebuds_api_state.dart';
import 'package:bikebuds/client_state_entity_state.dart';
import 'package:bikebuds/config.dart';
import 'package:bikebuds/firebase_messaging.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/main_screen.dart';
import 'package:bikebuds/pages/measures/measures_state.dart';
import 'package:bikebuds/sign_in_screen.dart';
import 'package:bikebuds/storage/storage.dart';
import 'package:bikebuds/user_state.dart';
import 'package:bikebuds/widgets/loading.dart';
import 'package:bikebuds_api/api.dart' hide UserState;
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

const Color PRIMARY_COLOR = Color(0xFF03dac6);
const Color ACCENT_COLOR = Color(0xFFff4081);

/// Used to get a reference to the context inside the multi-providers.
final appDelegateGlobalKey = new GlobalKey();

/// Used to get a reference to the context inside the material app.
/// https://stackoverflow.com/a/54607515/3002848
final homeGlobalKey = new GlobalKey();

class App extends StatefulWidget {
  @override
  _AppState createState() => _AppState();
}

class _AppState extends State<App> {
  Future<bool> _loader;
  Config config;
  Storage storage;
  MeasuresState _measuresState = MeasuresState(filter: "weight");
  FirebaseOptions firebaseOptions;
  FirebaseState firebaseState;

  // Gotta hold onto this, so that it is not dereferenced and we stop listening.
  FirebaseMessaging firebaseMessaging = registerFirebaseMessaging();

  @override
  void initState() {
    _loader = _load().then((value) {
      print('App: _load: $value');
      return true;
    }, onError: (err) => print('App: _load: failed: $err'));

    super.initState();
  }

  Future<bool> _load() async {
    config = await loadConfig(context);

    storage = await Storage.load();
    print('App: _load: storage: $storage');

    firebaseOptions = await loadFirebaseOptions(context);
    firebaseState = FirebaseState(config, firebaseOptions);
    var firebaseResult = await firebaseState.load();
    print('App: _load: firebase: $firebaseResult');
    return true;
  }

  @override
  Widget build(BuildContext context) {
    print('App: build in Isolate#${shortHash(Isolate.current)}');
    return FutureBuilder<bool>(
        future: _loader,
        builder: (context, AsyncSnapshot<bool> snapshot) {
          if (!snapshot.hasData) {
            return Container();
          }
          return MultiProvider(providers: [
            Provider<Config>.value(value: config),
            Provider<Storage>.value(value: storage),
            ChangeNotifierProvider<FirebaseState>.value(value: firebaseState),
            ChangeNotifierProxyProvider2<Config, FirebaseState,
                    BikebudsApiState>(
                create: (_) => BikebudsApiState(),
                update: (_, config, firebaseState, bikebudsApiState) =>
                    bikebudsApiState
                      ..config = config
                      ..firebaseState = firebaseState),
            ChangeNotifierProxyProvider<BikebudsApiState, BikebudsClientState>(
                create: (_) => BikebudsClientState(),
                update: (_, bikebudsApiState, clientStateEntityState) =>
                    clientStateEntityState.update()),
            ChangeNotifierProxyProvider<FirebaseState, UserState>(
                create: (_) => UserState(),
                update: (_, firebaseState, userState) =>
                    userState..user = firebaseState.user),
            ChangeNotifierProxyProvider3<Storage, BikebudsApiState, UserState,
                    MeasuresState>(
                create: (_) => _measuresState,
                update:
                    (_, storage, bikebudsApiState, userState, measuresState) =>
                        measuresState
                          ..bikebudsApiState = bikebudsApiState
                          ..storage = storage
                          ..userState = userState)
          ], child: AppDelegate(appDelegateGlobalKey));
        });
  }
}

class AppDelegate extends StatelessWidget {
  AppDelegate(GlobalKey key) : super(key: key);

  @override
  Widget build(BuildContext context) {
    var firebaseState = Provider.of<FirebaseState>(context);
    print('AppDelegate: build: initialized: ${firebaseState.authInitialized},' +
        'signedIn: ${firebaseState.signedIn}');
    return firebaseState.signedIn
        ? SignedInApp()
        : firebaseState.authInitialized
            ? SignedOutApp()
            : Container();
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
  StreamSubscription<String> _messagingListener;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    // Listen for auth changes.
    var firebase = Provider.of<FirebaseState>(context);
    var bikebuds = Provider.of<BikebudsApiState>(context);

    // TODO: Turn this into a stream.
    if (bikebuds.isReady && !this._bikebudsFetched) {
      this._bikebudsFetched = true;
      bikebuds.profile.then((profile) {
        Provider.of<UserState>(context, listen: false)..profile = profile;
      }).catchError((err, stack) {
        print('$this: Failed to fetch profile: $err, $stack');
      });
    }

    // Register FCM.
    if (!kIsWeb && bikebuds.isReady && _messagingListener == null) {
      _registerFirebaseMessagingClient(firebase);
    }

    // TODO: Check the profile here, look for signup_complete and block
    // full-app rendering if we aren't signed up.
    //User user = UserModel.of(context)?.bikebudsUser;
  }

  void _registerFirebaseMessagingClient(FirebaseState firebase) async {
    print('App.FirebaseMessaging: registerFirebaseMessagingClient');
    _messagingListener = firebase.messaging.onTokenRefresh
        .listen(_onFirebaseMessagingTokenChanged);
    firebase.messaging
        .getToken()
        .then(_onFirebaseMessagingTokenChanged)
        .catchError((err, stack) =>
            print('App.FirebaseMessaging: getToken: Failed: $err, $stack'));
  }

  void _onFirebaseMessagingTokenChanged(token) {
    print('App.FirebaseMessaging: _onFirebaseMessagingTokenChanged');
    var bikebuds = Provider.of<BikebudsApiState>(context, listen: false);
    bikebuds.registerClient(token).then((ClientStateEntity response) {
      print('App.FirebaseMessaging: bikebuds.registerClient: Complete');
      Provider.of<BikebudsClientState>(context, listen: false)
        ..client = response;
    }).catchError((err, stack) => print(
        'App.FirebaseMessaging: bikebuds.registerClient: Failed: $err, $stack'));
  }

  @override
  void dispose() {
    if (_messagingListener != null) {
      _messagingListener.cancel();
    }
    super.dispose();
  }

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
      initialRoute: '/',
      routes: <String, WidgetBuilder>{
        '/': (BuildContext context) => Home(homeGlobalKey),
      },
    );
  }
}

class Home extends StatelessWidget {
  Home(Key key) : super(key: key);

  @override
  Widget build(BuildContext context) {
    var bikebuds = Provider.of<BikebudsApiState>(context);
    return bikebuds.isReady
        ? MainScreen()
        : Loading(message: "Loading bikebuds...");
  }
}

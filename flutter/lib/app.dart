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
import 'package:bikebuds/client_state_entity_state.dart';
import 'package:bikebuds/config.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/main_content.dart';
import 'package:bikebuds/main_screen.dart';
import 'package:bikebuds/pages/measures/measures_state.dart';
import 'package:bikebuds/sign_in_screen.dart';
import 'package:bikebuds/storage/storage.dart';
import 'package:bikebuds/user_state.dart';
import 'package:bikebuds/widgets/loading.dart';
import 'package:bikebuds_api/api.dart' hide UserState;
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

const Color PRIMARY_COLOR = Color(0xFF03dac6);
const Color ACCENT_COLOR = Color(0xFFff4081);

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

    storage = Storage();
    var storageResult = await storage.load();
    print('App: _load: storage: $storageResult');

    firebaseOptions = await loadFirebaseOptions(context);
    firebaseState = FirebaseState(config, firebaseOptions);
    var firebaseResult = await firebaseState.load();
    print('App: _load: firebase: $firebaseResult');
    return true;
  }

  @override
  Widget build(BuildContext context) {
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
      registerFirebaseMessaging(firebase, bikebuds);
    }

    // TODO: Check the profile here, look for signup_complete and block
    // full-app rendering if we aren't signed up.
    //User user = UserModel.of(context)?.bikebudsUser;
  }

  void registerFirebaseMessaging(
      FirebaseState firebase, BikebudsApiState bikebuds) async {
    _messagingListener = firebase.messaging.onTokenRefresh.listen((token) {
      bikebuds.registerClient(token).then((ClientStateEntity response) {
        print('SignedInApp: bikebuds.registerClient: Complete');
        Provider.of<BikebudsClientState>(context, listen: false)
          ..client = response;
      }).catchError((err, stack) {
        print('SignedInApp: bikebuds.registerClient: Failed: $err, $stack');
      });
    });
    try {
      await firebase.messaging.requestNotificationPermissions();
    } catch (err) {
      print('App: Could not request notification permissions: $err');
    }
    firebase.messaging.configure(
        onMessage: this.onMessage,
        onResume: this.onResume,
        onLaunch: this.onLaunch);
  }

  @override
  void dispose() {
    if (_messagingListener != null) {
      _messagingListener.cancel();
    }
    super.dispose();
  }

  // only called when the app is in the foreground.
  Future<dynamic> onMessage(Map<String, dynamic> message) async {
    print('Messaging.onMessage: $message');
    if (message.containsKey('data') && message['data'].containsKey('refresh')) {
      print('Messaging.onMessage: Refresh: ${message['data']['refresh']}');
      switch (message['data']['refresh']) {
        case 'weight':
          try {
            await Provider.of<MeasuresState>(context, listen: false)
                .refresh(force: true);
            print('Messaging.onMessage: Refreshed weight');
          } catch (err, stack) {
            print('Messaging.onMessage: Unable to refresh: $err, $stack');
          }
          break;
        default:
          print('Messaging.onMessage: Unrecognized refresh');
      }
    }
    if (message.containsKey('notification') &&
        message['notification'].containsKey('title') &&
        (message['notification']['title'] as String).isNotEmpty &&
        message['notification'].containsKey('body') &&
        (message['notification']['body'] as String).isNotEmpty) {
      Scaffold.of(mainContentGlobalKey.currentContext).showSnackBar(
        SnackBar(
          content: ListTile(
            title: Text(message['notification']['title']),
            subtitle: Text(message['notification']['body']),
          ),
        ),
      );
    }
  }

  Future<dynamic> onResume(Map<String, dynamic> message) async {
    print('Messaging.onResume: $message');
  }

  Future<dynamic> onLaunch(Map<String, dynamic> message) async {
    print('Messaging.onLaunch: $message');
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

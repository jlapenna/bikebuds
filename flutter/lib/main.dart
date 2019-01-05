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
import 'dart:convert';

import 'package:bikebuds/firebase_http_client.dart';
import 'package:bikebuds/splash_screen.dart';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:bikebuds_api/bikebuds/v1.dart';

void main() => runApp(MyApp());

final FirebaseAuth _auth = FirebaseAuth.instance;
final GoogleSignIn _googleSignIn = GoogleSignIn();
final FirebaseMessaging _firebaseMessaging = FirebaseMessaging();

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bikebuds',
      theme: ThemeData(
        primaryColor: Color(0xFF03dac6),
        accentColor: Color(0xFFff4081),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => SplashScreen(_auth, _googleSignIn, _firebaseMessaging,
            title: 'Bikebuds'),
        '/home': (context) => HomeScreen(title: 'Bikebuds'),
      },
    );
  }
}

class HomeScreen extends StatefulWidget {
  HomeScreen({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Future<dynamic> _googleServicesJson;
  StreamSubscription<FirebaseUser> _listener;

  FirebaseUser _firebaseUser;
  BikebudsApi _api;
  var _loadingAthlete = false;
  SharedDatastoreAthletesAthleteMessage _athlete;

  _HomeScreenState();

  @override
  void initState() {
    super.initState();
    _googleServicesJson = _loadGoogleServicesJson();
    _listener = _auth.onAuthStateChanged.listen(_onAuthStateChanged);

    _firebaseMessaging.configure(
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

    _firebaseMessaging.getToken().then((token) {
      print('on token $token');
    });
  }

  Future<dynamic> _loadGoogleServicesJson() async {
    return json.decode(await DefaultAssetBundle.of(context)
        .loadString("android/app/google-services.json"));
  }

  void _onAuthStateChanged(user) async {
    print("Auth State Changed: $user");
    setState(() {
      _firebaseUser = user;
    });

    // We don't setState for the API because it alone isn't enough to
    // trigger a rebuild.
    var googleServicesJson = await _googleServicesJson;
    String key = googleServicesJson['client'][0]['api_key'][0]['current_key'];
    var token = await user.getIdToken(refresh: true);
    _api = BikebudsApi(FirebaseHttpClient(key, token));

    if (!_loadingAthlete) {
      _loadingAthlete = true;
      _api.getProfile(MainRequest()).then((response) {
        setState(() {
          _athlete = response.athlete;
        });
      });
    }
  }

  @override
  void dispose() {
    _listener?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    String name = _firebaseUser == null
        ? "Unexpected..."
        : (_firebaseUser?.displayName ?? _firebaseUser?.email);
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            _athlete?.profile == null
                ? Text("Photo")
                : Image.network(_athlete?.profile),
            Text(name),
            Text(_athlete?.city ?? ""),
          ],
        ),
      ),
    );
  }
}

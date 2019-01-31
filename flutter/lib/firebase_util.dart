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

import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/widgets.dart';

class FirebaseSignInState {
  final FirebaseUser user;
  final FirebaseUser userNext;

  FirebaseSignInState(this.user, this.userNext);

  @override
  String toString() {
    return 'FirebaseUsers(${user?.uid}, ${userNext?.uid})';
  }

  get signedIn => user != null && userNext != null;
}

class FirebaseState {
  final FirebaseApp app;
  final FirebaseAuth auth;
  final FirebaseMessaging messaging;

  FirebaseApp appNext;
  FirebaseAuth authNext;
  Firestore firestore;

  FirebaseState(
      {@required this.app, @required this.auth, @required this.messaging});

  @override
  String toString() {
    return 'FirebaseState(${app?.name}, ${appNext?.name})';
  }

  registerMessaging() {
    if (messaging == null) {
      return;
    }
    messaging.configure(
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
  }
}

Future<FirebaseState> loadFirebase(BuildContext context) async {
  print('loadFirebase');
  var state = _loadDefaultFirebase();
  var loadedJson = await json.decode(await DefaultAssetBundle.of(context)
      .loadString("android/app/google-services-next-android.json"));
  FirebaseOptions options = _toFirebaseOptions(loadedJson);
  try {
    state.appNext = await FirebaseApp.configure(name: "next", options: options);
  } catch (e) {
    state.appNext = await FirebaseApp.appNamed("next");
  }

  state.authNext = FirebaseAuth.fromApp(state.appNext);
  state.firestore = Firestore(app: state.appNext);
  print('loadFirebase: $state');
  return Future.value(state);
}

FirebaseState _loadDefaultFirebase() {
  var app = FirebaseApp.instance;
  var auth = FirebaseAuth.instance;
  var messaging = FirebaseMessaging();
  return FirebaseState(app: app, auth: auth, messaging: messaging);
}

FirebaseOptions _toFirebaseOptions(dynamic config) {
  // https://firebase.google.com/docs/reference/swift/firebasecore/api/reference/Classes/FirebaseOptions
  return FirebaseOptions(
      googleAppID: config['client'][0]['client_info']['mobilesdk_app_id'],
      apiKey: config['client'][0]['api_key'][0]['current_key'], // iOS API Key?
      bundleID: "bikebuds.cc", // iOS Bundle ID
      clientID: null, // iOS Client ID
      trackingID: null, // Analytics Tracking ID
      gcmSenderID: config['project_info']['project_number'],
      projectID: config['project_info']['project_id'],
      androidClientID: config['client'][0]['oauth_client'][0]['client_id'],
      databaseURL: config['project_info']['firebase_url'],
      deepLinkURLScheme: null, // Durable Deep Link service
      storageBucket: config['project_info']['storage_bucket']);
}
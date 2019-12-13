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

import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/widgets.dart';

class FirebaseSignInState with ChangeNotifier {
  FirebaseState _firebaseState;
  FirebaseUser user;
  FirebaseUser userNext;
  bool _initialized = false;
  bool _disposed = false;

  @override
  dispose() {
    _disposed = true;
    _firebaseState.removeListener(_onFirebaseStateChanged);
    super.dispose();
  }

  @override
  String toString() {
    return 'FirebaseSignInState($_initialized, ${user?.uid}, ${userNext?.uid})';
  }

  set firebaseState(FirebaseState value) {
    if (_firebaseState != null) {
      _firebaseState.removeListener(_onFirebaseStateChanged);
    }
    _firebaseState = value;
    _firebaseState.addListener(_onFirebaseStateChanged);
  }

  void _onFirebaseStateChanged() async {
    if (_firebaseState.isLoaded()) {
      var firebaseUserFuture = _firebaseState.auth.currentUser();
      var firebaseNextUserFuture = _firebaseState.authNext.currentUser();
      this.update(await firebaseUserFuture, await firebaseNextUserFuture);
    }
  }

  void update(FirebaseUser user, FirebaseUser userNext) {
    _initialized = true;
    this.user = user;
    this.userNext = userNext;
    if (!_disposed) {
      notifyListeners();
    }
  }

  get isInitialized => _initialized;
  get signedIn => user != null && userNext != null;
}

class FirebaseState with ChangeNotifier {
  final FirebaseApp app = FirebaseApp.instance;
  final FirebaseAuth auth = FirebaseAuth.instance;
  final FirebaseMessaging messaging = FirebaseMessaging();

  FirebaseApp appNext;
  FirebaseAuth authNext;
  Firestore firestore;

  FirebaseState(BuildContext context) {
    _loadFirebase(context);
  }

  bool isLoaded() {
    return app != null && appNext != null;
  }

  _loadFirebase(BuildContext context) async {
    var loadedJson = await json.decode(await DefaultAssetBundle.of(context)
        .loadString("android/app/google-services-next-android.json"));
    FirebaseOptions options = _toFirebaseOptions(loadedJson);
    var appNext = await _loadAppNext(options);
    var authNext = FirebaseAuth.fromApp(appNext);
    var firestore = Firestore(app: appNext);
    this.appNext = appNext;
    this.authNext = authNext;
    this.firestore = firestore;
    notifyListeners();
  }

  FirebaseOptions _toFirebaseOptions(dynamic config) {
    // https://firebase.google.com/docs/reference/swift/firebasecore/api/reference/Classes/FirebaseOptions
    return FirebaseOptions(
        googleAppID: config['client'][0]['client_info']['mobilesdk_app_id'],
        apiKey: config['client'][0]['api_key'][0]['current_key'], // iOS Key?
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

  Future<FirebaseApp> _loadAppNext(FirebaseOptions options) async {
    try {
      return await FirebaseApp.configure(name: "next", options: options);
    } catch (e) {
      return await FirebaseApp.appNamed("next");
    }
  }
}

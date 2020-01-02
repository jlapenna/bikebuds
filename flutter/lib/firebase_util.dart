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
import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';

class FirebaseSignInState with ChangeNotifier {}

class FirebaseState with ChangeNotifier {
  bool _authInitialized = false;
  final FirebaseApp _app = FirebaseApp.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FirebaseMessaging messaging = FirebaseMessaging();

  bool _disposed = false;

  bool _authInitializedNext = false;
  FirebaseApp _appNext;
  FirebaseAuth _authNext;

  StreamSubscription<FirebaseUser> _sub;
  StreamSubscription<FirebaseUser> _subNext;

  Firestore firestore;
  FirebaseUser user;
  FirebaseUser userNext;

  FirebaseState(BuildContext context) {
    _loadFirebase(context);
  }

  @override
  String toString() {
    return 'FirebaseState($_app, $_appNext)#${shortHash(this)}';
  }

  @override
  dispose() {
    if (_sub != null) {
      _sub.cancel();
      _sub = null;
    }
    if (_subNext != null) {
      _subNext.cancel();
      _subNext = null;
    }
    super.dispose();
  }

  _loadFirebase(BuildContext context) async {
    var loadedJson = await json.decode(await DefaultAssetBundle.of(context)
        .loadString("android/app/google-services-next-android.json"));
    FirebaseOptions options = _toFirebaseOptions(loadedJson);

    var appNext = await _loadAppNext(options);
    var authNext = FirebaseAuth.fromApp(appNext);
    var firestore = Firestore(app: appNext);
    // Only after we have all three components do we assign.
    this._appNext = appNext;
    this._authNext = authNext;
    this.firestore = firestore;
    _auth.currentUser().then((firebaseUser) {
      // Only after we're set up for firebase do we listen.
      _sub = _auth.onAuthStateChanged.listen(_onAuthStateChanged);
      _subNext = _authNext.onAuthStateChanged.listen(_onAuthStateChangedNext);
    });

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

  _onAuthStateChanged(FirebaseUser firebaseUser) {
    this.user = firebaseUser;

    // We've processed at least one firebase auth event.
    this._authInitialized = true;
    if (!_disposed) {
      notifyListeners();
    }
  }

  _onAuthStateChangedNext(FirebaseUser firebaseUser) {
    this.userNext = firebaseUser;
    print('$this: onAuthStateChangedNext: ${user?.uid}, ${userNext?.uid}');

    // We've processed at least one firebase auth event.
    this._authInitializedNext = true;
    if (!_disposed) {
      notifyListeners();
    }
  }

  get options {
    try {
      return _app?.options;
    } catch (err) {
      // Its possible firebase failed to load (like with no net connectivity)
      // and it doesn't protect itself from NPEs.
      print('$this: Warning: Failed reading options: $err');
    }
  }

  get authInitialized => _authInitialized && _authInitializedNext;
  get loaded => _app != null && _appNext != null;
  get signedIn => user != null && userNext != null;

  signOut() {
    return Future.wait([_auth.signOut(), _authNext.signOut()]);
  }

  signInWithCredential(credential) {
    return _auth.signInWithCredential(credential);
  }

  signInWithCredentialNext(credential) {
    return _authNext.signInWithCredential(credential);
  }
}

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

import 'package:bikebuds/config.dart';
import 'package:bikebuds/fake_user_wrapper.dart';
import 'package:bikebuds/firebase_user_wrapper.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';

class FirebaseSignInState with ChangeNotifier {}

class FirebaseState with ChangeNotifier {
  final Config _config;
  final FirebaseOptions _firebaseOptions;

  bool _authInitialized = false;
  final FirebaseApp _app = FirebaseApp.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FirebaseMessaging messaging = FirebaseMessaging();

  bool _authInitializedNext = false;
  FirebaseApp _appNext;
  FirebaseAuth _authNext;

  StreamSubscription<FirebaseUser> _sub;
  StreamSubscription<FirebaseUser> _subNext;

  Firestore firestore;
  FirebaseUserWrapper user;
  FirebaseUserWrapper userNext;

  FirebaseState(this._config, this._firebaseOptions);

  String get apiKey => _firebaseOptions.apiKey;

  @override
  String toString() {
    return 'FirebaseState($_app, $_appNext, user=$userNext, userNext=$userNext)#${shortHash(this)}';
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

  load() async {
    var appNext = await _loadAppNext(_firebaseOptions);
    var authNext = FirebaseAuth.fromApp(appNext);
    var firestore = Firestore(app: appNext);
    // Only after we have all three components do we assign.
    this._appNext = appNext;
    this._authNext = authNext;
    this.firestore = firestore;

    // Notify because of all the things above.
    notifyListeners();

    if (_config.config['is_dev'] &&
        (_config.config['fake_user'] != null &&
            _config.config['fake_user'].isNotEmpty)) {
      this.user = FakeUserWrapper(displayName: _config.config['fake_user']);
      this.userNext = FakeUserWrapper(displayName: _config.config['fake_user']);
      this._authInitialized = true;

      // Notify because auth has changed (as would happen when
      // auth.onAuthStateChanged.listen callbacks occur.
      notifyListeners();
    } else {
      // Only after we're set up for firebase do we listen.
      _auth.currentUser().then((firebaseUser) {
        _sub = _auth.onAuthStateChanged.listen(_onAuthStateChanged);
      });
      _authNext.currentUser().then((firebaseUser) {
        _subNext = _authNext.onAuthStateChanged.listen(_onAuthStateChangedNext);
      });
    }

    return this;
  }

  Future<FirebaseApp> _loadAppNext(FirebaseOptions options) async {
    try {
      return await FirebaseApp.configure(name: "next", options: options);
    } catch (e) {
      return await FirebaseApp.appNamed("next");
    }
  }

  _onAuthStateChanged(FirebaseUser firebaseUser) {
    this.user = FirebaseUserWrapper(firebaseUser);

    // We've processed at least one firebase auth event.
    this._authInitialized = true;
    notifyListeners();
  }

  _onAuthStateChangedNext(FirebaseUser firebaseUser) {
    this.userNext = FirebaseUserWrapper(firebaseUser);

    // We've processed at least one firebase auth event.
    this._authInitializedNext = true;
    notifyListeners();
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

Future<FirebaseOptions> loadFirebaseOptions(BuildContext context) async {
  var loadedJson = await json.decode(await DefaultAssetBundle.of(context)
      .loadString("android/app/google-services-next-android.json"));
  return _toFirebaseOptions(loadedJson);
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

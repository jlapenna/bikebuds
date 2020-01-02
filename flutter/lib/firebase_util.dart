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

class FirebaseSignInState with ChangeNotifier {
  FirebaseState _firebaseState;
  bool _disposed = false;

  FirebaseUser user;
  FirebaseUser userNext;

  @override
  dispose() {
    _disposed = true;
    _firebaseState.removeListener(_onFirebaseStateChanged);
    super.dispose();
  }

  @override
  String toString() {
    return 'FirebaseSignInState(${user?.uid}, ${userNext?.uid})#${shortHash(this)}';
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
      var firebaseUserFuture = _firebaseState._auth.currentUser();
      var firebaseNextUserFuture = _firebaseState._authNext.currentUser();
      this._update(await firebaseUserFuture, await firebaseNextUserFuture);
    }
  }

  void _update(FirebaseUser user, FirebaseUser userNext) {
    print('$this: _update: ${user?.uid}, ${userNext?.uid}');
    this.user = user;
    this.userNext = userNext;
    if (!_disposed) {
      notifyListeners();
    }
  }

  void signIn(FirebaseUser user, FirebaseUser userNext) {
    this._update(user, userNext);
  }

  void signOut() {
    _update(null, null);
  }

  StreamSubscription<FirebaseUser> onAuthStateChanged(Function fn) {
    return _firebaseState._auth.onAuthStateChanged.listen(fn);
  }

  signInWithCredential(credential) {
    return _firebaseState._auth.signInWithCredential(credential);
  }

  signInWithCredentialNext(credential) {
    return _firebaseState._authNext.signInWithCredential(credential);
  }

  get signedIn => user != null && userNext != null;
}

class FirebaseState with ChangeNotifier {
  final FirebaseApp _app = FirebaseApp.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FirebaseMessaging messaging = FirebaseMessaging();
  Firestore firestore;

  FirebaseApp _appNext;
  FirebaseAuth _authNext;

  FirebaseState(BuildContext context) {
    _loadFirebase(context);
  }

  @override
  String toString() {
    return 'FirebaseState($_app, $_appNext)#${shortHash(this)}';
  }

  bool isLoaded() {
    return _app != null && _appNext != null;
  }

  _loadFirebase(BuildContext context) async {
    var loadedJson = await json.decode(await DefaultAssetBundle.of(context)
        .loadString("android/app/google-services-next-android.json"));
    FirebaseOptions options = _toFirebaseOptions(loadedJson);
    var appNext = await _loadAppNext(options);
    var authNext = FirebaseAuth.fromApp(appNext);
    var firestore = Firestore(app: appNext);
    this._appNext = appNext;
    this._authNext = authNext;
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

  get options {
    return _app.options;
  }
}

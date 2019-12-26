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

import "dart:async";
import 'dart:io';

import "package:bikebuds/config.dart";
import "package:bikebuds/firebase_util.dart";
import "package:bikebuds_api/api.dart";
import "package:flutter/widgets.dart";

class BikebudsApiState with ChangeNotifier {
  bool _disposed = false;

  Config _config;
  FirebaseSignInState _firebaseSignInState;
  FirebaseState _firebaseState;

  BikebudsApi _api = BikebudsApi(ApiClient());

  @override
  void dispose() {
    this._disposed = true;
    if (_firebaseSignInState != null) {
      _firebaseSignInState.removeListener(_listenFirebaseSignInState);
    }
    if (_firebaseState != null) {
      this._firebaseState.removeListener(_listenFirebaseState);
    }
    super.dispose();
  }

  @override
  toString() {
    return 'BikebudsApiState($isReady)';
  }

  set config(Config value) {
    assert(value != null);
    if (value == _config) {
      // No changes.
      return;
    }
    print('$this: config changed: $_config -> $value');

    // Assign the new value.
    _config = value;
    _api.apiClient.basePath = (_config).config["api_url"];

    if (!_disposed) {
      notifyListeners();
    }
  }

  set firebaseState(FirebaseState value) {
    assert(value != null);
    if (value == _firebaseState) {
      // No changes.
      return;
    }
    print('$this: firebaseState changed: $_firebaseState -> $value');

    // Remove the existing listener.
    if (_firebaseState != null) {
      _firebaseState.removeListener(_listenFirebaseState);
    }

    _firebaseState = value;
    _firebaseState.addListener(_listenFirebaseState);
    _listenFirebaseState();
  }

  _listenFirebaseState() async {
    print('$this: _listenFirebaseState');
    ApiKeyAuth apiKeyAuth = _api.apiClient.getAuthentication("api_key");
    apiKeyAuth.apiKey = (await _firebaseState.options).apiKey;

    if (!_disposed) {
      notifyListeners();
    }
  }

  set firebaseSignInState(FirebaseSignInState value) {
    assert(value != null);
    if (value == _firebaseSignInState) {
      // No changes.
      return;
    }
    print(
        '$this: firebaseSignInState changed: $_firebaseSignInState -> $value');

    // Remove the existing listener.
    if (_firebaseSignInState != null) {
      _firebaseSignInState.removeListener(_listenFirebaseSignInState);
    }

    // Assign the new value and listener.
    _firebaseSignInState = value;
    _firebaseSignInState.addListener(_listenFirebaseSignInState);
    _listenFirebaseSignInState();
  }

  _listenFirebaseSignInState() async {
    print('$this: _listenFirebaseSignInState');
    if (_firebaseSignInState.signedIn) {
      try {
        var firebaseUser = _firebaseSignInState.user;
        OAuth oAuth = _api.apiClient.getAuthentication("firebase");
        oAuth.accessToken = (await firebaseUser.getIdToken()).token;
      } catch (err) {
        print("$this: _listenFirebaseSignInState failed: $err");
      }
    }

    if (!_disposed) {
      notifyListeners();
    }
  }

  bool get isReady {
    return _config != null &&
        _firebaseState != null &&
        _firebaseSignInState != null &&
        _firebaseSignInState.signedIn;
  }

  Future<Profile> get profile {
    return _api.getProfile(xFields: "*");
  }

  Future<Auth> get auth {
    return _api.auth(xFields: "*");
  }

  Future<ClientStateEntity> registerClient(
      FutureOr<String> firebaseToken) async {
    var client = ClientState()
      ..token = await firebaseToken
      ..type = Platform.operatingSystem.toUpperCase();
    return _api.updateClient(client, xFields: "*").then((response) {
      return response;
    });
  }
}

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
import 'package:flutter/foundation.dart';
import "package:flutter/widgets.dart";

class BikebudsApiState with ChangeNotifier {
  bool _addedAuth = false;

  Config _config;
  FirebaseState _firebaseState;

  BikebudsApi _api = BikebudsApi(ApiClient());

  @override
  toString() {
    return 'BikebudsApiState($isReady)';
  }

  _listenFirebaseState() async {
    print('$this: _listenFirebaseState');
    ApiKeyAuth apiKeyAuth = _api.apiClient.getAuthentication("api_key");
    apiKeyAuth.apiKey = _firebaseState.apiKey;

    OAuth oAuth = _api.apiClient.getAuthentication("firebase");
    if (_config.config['is_dev'] && _config.config.containsKey('fake_user')) {
      print('$this: _listenFirebaseState: Using Fake User for token');
      oAuth.accessToken = 'XYZ_TOKEN';
      _addedAuth = true;
    } else if (_firebaseState.user != null) {
      try {
        var firebaseUser = _firebaseState.user;
        oAuth.accessToken = await firebaseUser.getAccessToken();
        _addedAuth = true;
      } catch (err, stack) {
        print("$this: _listenFirebaseState failed: $err: $stack");
      }
    }
    notifyListeners();
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

    notifyListeners();
  }

  set firebaseState(FirebaseState value) {
    assert(value != null);
    if (value == _firebaseState) {
      // No changes.
      return;
    }
    print('$this: firebaseState changed: $_firebaseState -> $value');
    _firebaseState = value;
    _listenFirebaseState();
  }

  bool get isReady {
    return _config != null && _addedAuth;
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

  Future<SeriesEntity> getSeries({filter}) {
    return _api.getSeries(filter: filter, xFields: "*");
  }
}

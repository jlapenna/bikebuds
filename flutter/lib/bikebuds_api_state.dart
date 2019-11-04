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
  bool _loading = false;

  Config _config;
  FirebaseState _firebaseState;
  FirebaseSignInState _signInState;

  BikebudsApi _api;

  @override
  void dispose() {
    this._disposed = true;
    this._firebaseState.removeListener(_update);
    this._signInState.removeListener(_update);
    super.dispose();
  }

  set config(Config value) {
    _config = value;
  }

  set firebaseState(FirebaseState value) {
    if (_firebaseState != null) {
      _firebaseState.removeListener(_update);
    }
    _firebaseState = value;
    _firebaseState.addListener(_update);
  }

  set signInState(FirebaseSignInState value) {
    if (_signInState != null) {
      _signInState.removeListener(_update);
    }
    _signInState = value;
    _signInState.addListener(_update);
  }

  _update() async {
    if (!_disposed &&
        !_loading &&
        _firebaseState.app != null &&
        _signInState.signedIn) {
      _loading = true;
      var apiClient = ApiClient(basePath: (_config).config["api_url"]);

      // Set an API Key.
      ApiKeyAuth apiKeyAuth = apiClient.getAuthentication("api_key");
      apiKeyAuth.apiKey = (await _firebaseState.app.options).apiKey;

      // Set an access token.
      var firebaseUser = await _firebaseState.auth.currentUser();
      OAuth oAuth = apiClient.getAuthentication("firebase");
      oAuth.accessToken = (await firebaseUser.getIdToken(refresh: true)).token;

      this._api = BikebudsApi(apiClient);
      if (!_disposed) {
        notifyListeners();
      }
    }
  }

  bool isReady() {
    return _api != null;
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

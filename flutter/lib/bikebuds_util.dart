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

import 'package:bikebuds/firebase_http_client.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds_api/bikebuds/v1.dart';
import 'package:firebase_auth/firebase_auth.dart';

class BikebudsState {
  final Map<String, dynamic> _config;
  final FirebaseContainerState _firebase;
  Future<BikebudsApi> _api;
  StreamSubscription<FirebaseUser> _unsubscribe;

  BikebudsState(config, firebase)
      : _config = config,
        _firebase = firebase {
    _unsubscribe =
        _firebase.auth.onAuthStateChanged.listen(_handleOnAuthStateChanged);
    _api = Future(() async {
      return BikebudsApi(await loadFromState(_firebase),
          rootUrl: (_config)['api_url'] + "/_ah/api/");
    });
  }

  _handleOnAuthStateChanged(FirebaseUser user) async {
    print('BikebudsState._handleOnAuthStateChanged: $user');
    _api = Future(() async => BikebudsApi(await loadFromState(_firebase)));
  }

  dispose() {
    if (_unsubscribe != null) {
      _unsubscribe.cancel();
    }
  }

  Future<FirebaseUser> get user async {
    return _firebase.auth.currentUser();
  }

  Future<MainProfileResponse> get profile async {
    return (await _api).getProfile(MainRequest());
  }

  Future<MainClientResponse> registerClient() async {
    var firebaseToken = await _firebase.messaging.getToken();
    var request = MainUpdateClientRequest()
      ..client = (SharedDatastoreUsersClientMessage()..id = firebaseToken);
    return (await _api).updateClient(request);
  }
}

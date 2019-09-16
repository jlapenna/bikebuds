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
import "package:bikebuds/sign_in_screen.dart";
import "package:bikebuds_api/api.dart";
import "package:firebase_auth/firebase_auth.dart";
import "package:flutter/widgets.dart";

class BikebudsApiContainer extends StatefulWidget {
  final Widget child;

  BikebudsApiContainer({@required this.child});

  static BikebudsApiContainerState of(BuildContext context) {
    return (context.inheritFromWidgetOfExactType(_InheritedBikebudsApiContainer)
            as _InheritedBikebudsApiContainer)
        .data;
  }

  @override
  BikebudsApiContainerState createState() => new BikebudsApiContainerState();
}

class BikebudsApiContainerState extends State<BikebudsApiContainer> {
  bool _loading = false;

  BikebudsApi _api;
  ClientStateEntity _client;

  @override
  void didChangeDependencies() {
    print('BikebudsApiContainerState.didChangeDependencies');
    var config = ConfigContainer.of(context).config;
    var firebase = FirebaseContainer.of(context);
    var signedIn = SignInContainer.of(context).signInState.signedIn;
    if (!_loading && config != null && firebase.app != null && signedIn) {
      _loadBikebudsApi();
    }
    super.didChangeDependencies();
  }

  _loadBikebudsApi() async {
    print("BikebudsApiContainerState._loadFirebase");
    _loading = true;
    var config = ConfigContainer.of(context).config;
    var firebase = FirebaseContainer.of(context);
    var apiClient = ApiClient(basePath: (config)["api_url"]);

    // Set an API Key.
    ApiKeyAuth apiKeyAuth = apiClient.getAuthentication("api_key");
    apiKeyAuth.apiKey = (await firebase.app.options).apiKey;

    // Set an access token.
    var firebaseUser = await firebase.auth.currentUser();
    OAuth oAuth = apiClient.getAuthentication("firebase");
    oAuth.accessToken = await firebaseUser.getIdToken(refresh: true);

    final api = BikebudsApi(apiClient);
    print("BikebudsApiContainerState._loadFirebase: $api");
    setState(() {
      this._api = api;
    });
  }

  @override
  Widget build(BuildContext context) {
    return new _InheritedBikebudsApiContainer(
      data: this,
      child: widget.child,
    );
  }

  bool isReady() {
    return _api != null;
  }

  Future<FirebaseUser> get user async {
    var firebase = FirebaseContainer.of(context);
    return firebase.auth.currentUser();
  }

  Future<Profile> get profile async {
    return _api.getProfile(xFields: "*");
  }

  Future<Auth> get auth async {
    return _api.auth(xFields: "*");
  }

  ClientStateEntity get clientState {
    return _client;
  }

  Future<ClientStateEntity> registerClient(
      FutureOr<String> firebaseToken) async {
    var client = ClientState()
      ..token = await firebaseToken
      ..type = Platform.operatingSystem.toUpperCase();
    return _api.updateClient(client, xFields: "*").then((response) {
      print('bikebuds_util: registerClient: response: $response');
      setState(() {
        _client = response;
      });
      return response;
    });
  }
}

class _InheritedBikebudsApiContainer extends InheritedWidget {
  // Data is your entire state. In our case just "User"
  final BikebudsApiContainerState data;

  // You must pass through a child and your state.
  const _InheritedBikebudsApiContainer({
    Key key,
    @required this.data,
    @required Widget child,
  }) : super(key: key, child: child);

  // This is a built in method which you can use to check if
  // any state has changed. If not, no reason to rebuild all the widgets
  // that rely on your state.
  @override
  bool updateShouldNotify(_InheritedBikebudsApiContainer old) => true;
}

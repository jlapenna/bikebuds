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

import 'package:bikebuds/firebase_util.dart';
import 'package:googleapis_auth/auth_io.dart';
import 'package:http/http.dart'
    show BaseClient, BaseRequest, Client, StreamedResponse;

class FirebaseHttpClient extends BaseClient {
  Client baseClient;
  Map<String, String> headers;

  FirebaseHttpClient(token, this.baseClient)
      : headers = {
          "Authorization": 'Bearer ' + token,
        };

  @override
  Future<StreamedResponse> send(BaseRequest request) {
    return sendWithHeaders(request);
  }

  Future<StreamedResponse> sendWithHeaders(BaseRequest request) {
    request.headers.addAll(headers);
    return baseClient.send(request);
  }
}

Future<FirebaseHttpClient> loadFromFuture(
    Future<FirebaseState> firebaseLoader) async {
  print('firebase_http_client.loadFromFuture');
  return loadFromState(await firebaseLoader);
}

Future<FirebaseHttpClient> loadFromState(FirebaseState firebaseState) async {
  print('firebase_http_client.loadFromState');
  var firebaseUser = await firebaseState.auth.currentUser();
  var token = await firebaseUser.getIdToken(refresh: true);
  var options = await firebaseState.app.options;
  String key = options.apiKey;
  return FirebaseHttpClient(token, clientViaApiKey(key));
}

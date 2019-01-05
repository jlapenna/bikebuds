/**
 * Copyright 2019 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import 'package:http/http.dart'
    show BaseRequest, BaseClient, Client, Request, StreamedResponse;

class FirebaseHttpClient extends BaseClient {
  String _encodedKey;
  Client _baseClient;
  Map<String, String> _headers;

  FirebaseHttpClient(key, token, [Client httpClient]) {
    _baseClient = httpClient == null ? new Client() : httpClient;
    _encodedKey = Uri.encodeQueryComponent(key);
    _headers = {
      "Authorization": 'Bearer ' + token,
    };
  }

  @override
  Future<StreamedResponse> send(BaseRequest request) {
    return sendWithKey(request);
  }

  Future<StreamedResponse> sendNoKey(BaseRequest request) {
    request.headers.addAll(_headers);
    return _baseClient.send(request);
  }

  Future<StreamedResponse> sendWithKey(BaseRequest request) {
    var url = request.url;
    if (url.queryParameters.containsKey('key')) {
      return new Future.error(new Exception(
          'Tried to make a HTTP request which has already a "key" query '
          'parameter. Adding the API key would override that existing value.'));
    }
    if (url.query == '') {
      url = url.replace(query: 'key=$_encodedKey');
    } else {
      url = url.replace(query: '${url.query}&key=$_encodedKey');
    }
    var modifiedRequest = Request(request.method, url);
    modifiedRequest.headers.addAll(_headers);
    return _baseClient.send(modifiedRequest);
  }
}

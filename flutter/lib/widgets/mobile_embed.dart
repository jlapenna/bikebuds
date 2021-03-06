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

import 'package:bikebuds/bikebuds_api_state.dart';
import 'package:bikebuds_api/api.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../config.dart';

enum AuthState {
  NOT_STARTED,
  FETCHING_TOKEN,
  FETCHED_TOKEN,
  LOADING_AUTH_URL,
  LOADED_AUTH_URL,
  AUTHENTICATED,
  FAILED
}

class MobileEmbed extends StatefulWidget {
  final String target;

  MobileEmbed(this.target);

  @override
  _MobileEmbedState createState() => _MobileEmbedState();
}

class _MobileEmbedState extends State<MobileEmbed> {
  final Map<String, dynamic> _eventHandlers = {};
  final Completer<WebViewController> _controllerCompleter =
      Completer<WebViewController>();

  Auth _auth;
  AuthState _authState = AuthState.NOT_STARTED;

  WebViewController _controller;
  MobileEmbedJsController _mobileEmbedJsController;

  _MobileEmbedState() {
    _eventHandlers['signedIn'] = (event, payload) async {
      print('MobileEmbed._eventHandlers.$event');
      setState(() {
        this._authState = AuthState.AUTHENTICATED;
      });
    };
    _controllerCompleter.future.then((WebViewController controller) {
      this.setState(() {
        print('MobileEmbed: controller.then: complete');
        this._controller = controller;
        this._mobileEmbedJsController = MobileEmbedJsController(controller);
      });
    });
  }

  void loadAuthUrl() {
    var colorType =
        Theme.of(context).brightness == Brightness.dark ? 'dark' : 'light';
    var config = Provider.of<Config>(context).config;
    Uri uri = Uri.parse(config["devserver_url"] + "/embed/auth").replace(
        queryParameters: {'token': this._auth.token, 'colorType': colorType});
    print('MobileEmbed.loadAuthUrl: ${uri.path}, ' +
        'hasToken: ${uri.queryParameters['token'] != null}, ' +
        'colorType: $colorType');
    this._controller.loadUrl(uri.toString());
    setState(() {
      this._authState = AuthState.LOADED_AUTH_URL;
    });
  }

  void buildAuthEval(BuildContext context) {
    print('MobileEmbed.buildAuthEval: ${this._authState}');
    switch (this._authState) {
      case AuthState.NOT_STARTED:
        setState(() {
          this._authState = AuthState.FETCHING_TOKEN;
        });
        var bikebuds = Provider.of<BikebudsApiState>(context);
        bikebuds.auth.then((Auth auth) {
          print('MobileEmbed: bikebuds.auth complete');
          this.setState(() {
            this._authState = AuthState.FETCHED_TOKEN;
            this._auth = auth;
          });
        }).catchError((err) {
          print('MobileEmbed: bikebuds.auth failed, $err');
          this.setState(() {
            this._authState = AuthState.FAILED;
          });
        });
        break;
      case AuthState.FETCHING_TOKEN:
        break;
      case AuthState.FETCHED_TOKEN:
        if (_controller != null) {
          setState(() {
            _authState = AuthState.LOADING_AUTH_URL;
          });
          loadAuthUrl();
        }
        break;
      case AuthState.LOADING_AUTH_URL:
        break;
      case AuthState.LOADED_AUTH_URL:
        break;
      case AuthState.AUTHENTICATED:
        this._mobileEmbedJsController.navigate(widget.target);
        break;
      case AuthState.FAILED:
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    print('MobileEmbed.build');
    buildAuthEval(context);

    return WebView(
      initialUrl: null,
      onPageFinished: (String url) {
        url = url.replaceFirst(RegExp('token=.+'), "token=REDACTED");
        print('MobileEmbed.onPageFinished: $url');
      },
      javascriptMode: JavascriptMode.unrestricted,
      javascriptChannels: Set.from([
        JavascriptChannel(
            name: 'MobileEmbedEventChannel',
            onMessageReceived: (JavascriptMessage message) {
              var jsonEvent = json.decode(message.message);
              print('MobileEmbed.onMessageReceived: EventChannel: $jsonEvent');
              this._eventHandlers[jsonEvent['event']](
                  jsonEvent['event'], jsonEvent['payload']);
            })
      ]),
      onWebViewCreated: (WebViewController controller) {
        print('MobileEmbed: onWebViewCreated');
        _controllerCompleter.complete(controller);
      },
    );
  }
}

class MobileEmbedJsController {
  WebViewController _controller;

  MobileEmbedJsController(this._controller);

  Future<bool> doSomething() async {
    print('MobileEmbed: doSomething');
    return json.decode(await this
        ._controller
        .evaluateJavascript("window.MobileEmbed.doSomething()"));
  }

  Future<bool> navigate(String dest) async {
    print('MobileEmbed: navigate: $dest');
    return json.decode(await this
        ._controller
        .evaluateJavascript("window.MobileEmbed.navigate('$dest')"));
  }
}

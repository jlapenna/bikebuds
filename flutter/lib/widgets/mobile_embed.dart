// copyright 2019 google inc. all rights reserved.
//
// licensed under the apache license, version 2.0 (the "license");
// you may not use this file except in compliance with the license.
// you may obtain a copy of the license at
//
//     http://www.apache.org/licenses/license-2.0
//
// unless required by applicable law or agreed to in writing, software
// distributed under the license is distributed on an "as is" basis,
// without warranties or conditions of any kind, either express or implied.
// see the license for the specific language governing permissions and
// limitations under the license.

import 'dart:async';
import 'dart:convert';

import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds_api/api.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../config.dart';

enum AuthState {
  UNDEFINED,
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
  AuthState _authState = AuthState.UNDEFINED;

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
    final config = ConfigContainer.of(context).config;
    Uri url = Uri.parse(config["devserver_url"] + "/embed/auth")
        .replace(queryParameters: {'token': this._auth.token});
    print('MobileEmbed.loadAuthUrl: ${url.path}, ' +
        'hasToken: ${url.queryParameters['token'] != null}');
    this._controller.loadUrl(url.toString());
    setState(() {
      this._authState = AuthState.LOADED_AUTH_URL;
    });
  }

  void buildAuthEval(BuildContext context) {
    print('MobileEmbed.buildAuthEval: ${this._authState}');
    switch (this._authState) {
      case AuthState.UNDEFINED:
        setState(() {
          this._authState = AuthState.FETCHING_TOKEN;
        });
        var bikebuds = BikebudsApiContainer.of(context);
        bikebuds.auth.then((Auth auth) {
          print('MobileEmbed: bikebuds.auth complete');
          this.setState(() {
            this._authState = AuthState.FETCHED_TOKEN;
            this._auth = auth;
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

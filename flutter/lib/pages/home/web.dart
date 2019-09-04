import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../config.dart';

class Web extends StatefulWidget {
  @override
  _WebState createState() => _WebState();
}

class _WebState extends State<Web> {
  Completer<WebViewController> _controllerCompleter =
      Completer<WebViewController>();
  WebViewController _controller;
  WebJsInterface _jsInterface;

  Map<String, dynamic> _eventHandlers;

  _WebState() {
    this._eventHandlers = {
      'componentDidMount': (event, payload) async {
        print('Web._eventHandlers.$event');
        var result = await _jsInterface.loadCredentials("FAKE CREDENTIALS");
        print(
            'Web._eventHandlers.componentDidMount: loadCredentials: ${result}');
      },
    };
  }

  @override
  void initState() {
    super.initState();
    _controllerCompleter.future.then((WebViewController controller) {
      this.setState(() {
        this._controller = controller;
        this._jsInterface = WebJsInterface(controller);
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final config = ConfigContainer.of(context).config;
    final url = config["devserver_url"] + "/auth";
    return WebView(
      initialUrl: url,
      javascriptMode: JavascriptMode.unrestricted,
      javascriptChannels: Set.from([
        JavascriptChannel(
            name: 'MobileApp',
            onMessageReceived: (JavascriptMessage message) {
              var jsonEvent = json.decode(message.message);
              print('Web.onMessageReceived: $jsonEvent');
              this._eventHandlers[jsonEvent['event']](
                  jsonEvent['event'], jsonEvent['payload']);
            })
      ]),
      onWebViewCreated: (WebViewController controller) {
        print('Web.onWebViewCreated');
        _controllerCompleter.complete(controller);
      },
    );
  }
}

class WebJsInterface {
  WebViewController _controller;
  WebJsInterface(this._controller);

  Future<bool> loadCredentials(dynamic credentials) async {
    return json.decode(await this
        ._controller
        .evaluateJavascript("loadCredentials('$credentials')"));
  }
}

import 'dart:async';
import 'dart:convert';

import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds_api/api.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../config.dart';

class MobileEmbed extends StatefulWidget {
  @override
  _MobileEmbedState createState() => _MobileEmbedState();
}

class _MobileEmbedState extends State<MobileEmbed> {
  final Completer<WebViewController> _controllerCompleter =
      Completer<WebViewController>();

  WebViewController _controller;
  MobileEmbedJsInterface _jsInterface;
  String _token = "";

  final Map<String, dynamic> _eventHandlers = {
    'somethingHappened': (event, payload) async {
      print('MobileEmbed._eventHandlers.$event');
    },
  };

  _MobileEmbedState();

  @override
  void initState() {
    super.initState();
    _controllerCompleter.future.then((WebViewController controller) {
      this.setState(() {
        this._controller = controller;
      });
      var bikebuds = BikebudsApiContainer.of(context);
      print('MobileEmbed.initstate: controller: ${bikebuds}');
      bikebuds.auth.then((Auth auth) {
        print('MobileEmbed.auth: $auth');
        this.setState(() {
          this._token = auth.token;
        });
        final config = ConfigContainer.of(context).config;
        final url = config["devserver_url"] + "/embed/auth?token=" + auth.token;
        print('MobileEmbed.navigate: $url');
        controller.loadUrl(url);
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final config = ConfigContainer.of(context).config;
    final url = config["devserver_url"] + "/embed/auth?token=";
    return WebView(
      initialUrl: url,
      javascriptMode: JavascriptMode.unrestricted,
      javascriptChannels: Set.from([
        JavascriptChannel(
            name: 'EventChannel',
            onMessageReceived: (JavascriptMessage message) {
              var jsonEvent = json.decode(message.message);
              print('MobileEmbed.onMessageReceived: EventChannel: $jsonEvent');
              this._eventHandlers[jsonEvent['event']](
                  jsonEvent['event'], jsonEvent['payload']);
            })
      ]),
      onWebViewCreated: (WebViewController controller) {
        print('MobileEmbed.onWebViewCreated');
        _controllerCompleter.complete(controller);
      },
    );
  }
}

class MobileEmbedJsInterface {
  WebViewController _controller;

  MobileEmbedJsInterface(this._controller);

  Future<bool> doSomething() async {
    return json
        .decode(await this._controller.evaluateJavascript("doSomething()"));
  }
}

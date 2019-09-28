import 'dart:async';
import 'dart:convert';

import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds/loading.dart';
import 'package:bikebuds_api/api.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../config.dart';

class MobileEmbed extends StatefulWidget {
  @override
  _MobileEmbedState createState() => _MobileEmbedState();
}

class _MobileEmbedState extends State<MobileEmbed> {
  final Completer<WebViewController> _controllerCompleter =
      Completer<WebViewController>();

  bool _authenticated = false;
  WebViewController _controller;

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
      print('MobileEmbed.initstate: controller: $bikebuds');
      bikebuds.auth.then((Auth auth) {
        print('MobileEmbed.auth: $auth');
        if (auth != null && auth.token != null) {
          final config = ConfigContainer.of(context).config;
          final url =
              config["devserver_url"] + "/embed/auth?token=" + auth.token;
          print('MobileEmbed.navigate: $url');
          controller.loadUrl(url);
          setState(() {
            this._authenticated = true;
          });
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final config = ConfigContainer.of(context).config;
    final url = config["devserver_url"] + "/embed/auth?token=";
    return Visibility(
        visible: this._authenticated,
        replacement: loadingWidget(context),
        maintainInteractivity: true,
        maintainAnimation: true,
        maintainState: true,
        maintainSize: true,
        child: WebView(
          initialUrl: url,
          javascriptMode: JavascriptMode.unrestricted,
          javascriptChannels: Set.from([
            JavascriptChannel(
                name: 'EventChannel',
                onMessageReceived: (JavascriptMessage message) {
                  var jsonEvent = json.decode(message.message);
                  print(
                      'MobileEmbed.onMessageReceived: EventChannel: $jsonEvent');
                  this._eventHandlers[jsonEvent['event']](
                      jsonEvent['event'], jsonEvent['payload']);
                })
          ]),
          onWebViewCreated: (WebViewController controller) {
            print('MobileEmbed.onWebViewCreated');
            _controllerCompleter.complete(controller);
          },
        ));
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

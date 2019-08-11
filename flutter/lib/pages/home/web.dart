import 'dart:async';

import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../config.dart';

class Web extends StatefulWidget {
  @override
  _WebState createState() => _WebState();
}

class _WebState extends State<Web> {
  Completer<WebViewController> _controller = Completer<WebViewController>();
  @override
  Widget build(BuildContext context) {
    final config = ConfigContainer.of(context).config;
    final url = config["devserver_url"] + "/embed";
    return WebView(
      initialUrl: url,
      javascriptMode: JavascriptMode.unrestricted,
      javascriptChannels: Set.from([
        JavascriptChannel(
            name: 'Print',
            onMessageReceived: (JavascriptMessage message) {
              print(message.message);
            })
      ]),
      onWebViewCreated: (WebViewController webViewController) {
        _controller.complete(webViewController);
      },
    );
  }
}

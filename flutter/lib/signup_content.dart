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

import 'package:bikebuds/config.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class SignupContent extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    var config = ConfigContainer.of(context);
    var initialUrl = config.config['frontend_url'] + '/signup';
    if (config.config['is_dev']) {
      initialUrl = config.config['devserver_url'] + '/signup';
    }
    print('SignupContent: build: $initialUrl');
    return Center(
        child: WebView(
            initialUrl: initialUrl,
            javascriptMode: JavascriptMode.unrestricted));
  }
}

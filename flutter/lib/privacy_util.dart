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

import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:url_launcher/url_launcher.dart';

showPrivacyDialog(BuildContext context) {
  showDialog(
    context: context,
    builder: _builder,
  );
}

Widget _builder(BuildContext context) {
  return AlertDialog(
    content: Column(
      children: <Widget>[
        ListTile(
          title: Text("Terms of Service"),
          onTap: () {
            launch("https://bikebuds.com/tos");
            Navigator.pop(context);
          },
        ),
        ListTile(
          title: Text("Privacy Policy"),
          onTap: () {
            launch("https://bikebuds.com/privacy");
            Navigator.pop(context);
          },
        ),
      ],
    ),
  );
}

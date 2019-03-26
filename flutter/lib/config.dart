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

import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter/widgets.dart';

Future<Map<String, dynamic>> loadConfig() async {
  return json.decode(await rootBundle.loadString("config.json"));
}

class ConfigContainer extends InheritedWidget {
  final Map<String, dynamic> config;

  ConfigContainer({Key key, @required Widget child, @required this.config})
      : super(key: key, child: child);

  @override
  bool updateShouldNotify(InheritedWidget oldWidget) => true;

  static ConfigContainer of(BuildContext context) =>
      context.inheritFromWidgetOfExactType(ConfigContainer);
}

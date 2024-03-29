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

import 'package:flutter/widgets.dart';

class Config {
  final Map<String, dynamic> config;

  const Config(this.config);

  @override
  toString() {
    return 'Config(length: ${config.keys.length})';
  }
}

Future<Config> loadConfig(BuildContext context) {
  return DefaultAssetBundle.of(context)
      .loadString("config.json")
      .then(json.decode)
      .then((config) {
    return Config(config);
  });
}

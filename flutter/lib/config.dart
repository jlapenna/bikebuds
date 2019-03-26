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

class ConfigContainer extends StatefulWidget {
  final Widget child;
  final Map<String, dynamic> config;

  ConfigContainer({
    @required this.child,
    this.config,
  });

  static ConfigContainerState of(BuildContext context) {
    return (context.inheritFromWidgetOfExactType(_InheritedConfigContainer)
            as _InheritedConfigContainer)
        .data;
  }

  @override
  ConfigContainerState createState() => new ConfigContainerState();
}

class ConfigContainerState extends State<ConfigContainer> {
  Map<String, dynamic> config;

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  _loadConfig() async {
    print('ConfigContainerState._loadConfig');
    var loadedConfig = json.decode(await rootBundle.loadString("config.json"));
    setState(() {
      this.config = loadedConfig;
    });
  }

  @override
  Widget build(BuildContext context) {
    print('ConfigContainerState.build');
    return new _InheritedConfigContainer(
      data: this,
      child: widget.child,
    );
  }
}

class _InheritedConfigContainer extends InheritedWidget {
  // Data is your entire state. In our case just 'User'
  final ConfigContainerState data;

  // You must pass through a child and your state.
  const _InheritedConfigContainer({
    Key key,
    @required this.data,
    @required Widget child,
  }) : super(key: key, child: child);

  // This is a built in method which you can use to check if
  // any state has changed. If not, no reason to rebuild all the widgets
  // that rely on your state.
  @override
  bool updateShouldNotify(_InheritedConfigContainer old) => true;
}

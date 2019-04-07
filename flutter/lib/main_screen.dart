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
import 'package:bikebuds/events_content.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/privacy_util.dart';
import 'package:bikebuds/settings_content.dart';
import 'package:flutter/material.dart';

class MainScreen extends StatefulWidget {
  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedDrawerItem = 1;

  @override
  Widget build(BuildContext context) {
    var config = ConfigContainer.of(context).config;
    var firebase = FirebaseContainer.of(context);
    print('MainScreen.build: $config, $firebase');
    return Scaffold(
      appBar: AppBar(
        title: Text("Bikebuds"),
      ),
      drawer: buildDrawer(firebase),
      body: buildBody(firebase),
    );
  }

  Drawer buildDrawer(FirebaseContainerState firebase) {
    return Drawer(
      child: Column(
        children: <Widget>[
          Expanded(
            child: ListView(
              // Important: Remove any padding from the ListView.
              padding: EdgeInsets.zero,
              children: <Widget>[
                DrawerHeader(child: Container()),
                ListTile(
                  title: Text('Rides'),
                  onTap: () {
                    setState(() {
                      _selectedDrawerItem = 0;
                      Navigator.pop(context);
                    });
                  },
                ),
                ListTile(
                  title: Text('Settings'),
                  onTap: () {
                    setState(() {
                      _selectedDrawerItem = 1;
                      Navigator.pop(context);
                    });
                  },
                ),
              ],
            ),
          ),
          Container(
            child: Align(
              alignment: FractionalOffset.bottomCenter,
              child: Container(
                child: Column(
                  children: <Widget>[
                    Divider(),
                    ListTile(
                      title: Center(
                        child: Text('ToS - Privacy'),
                      ),
                      onTap: () {
                        Navigator.pop(context);
                        showPrivacyDialog(context);
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget buildBody(FirebaseContainerState firebase) {
    switch (_selectedDrawerItem) {
      case 0:
        return EventsContent();
      case 1:
        return SettingsContent();
      default:
        return Container();
    }
  }
}

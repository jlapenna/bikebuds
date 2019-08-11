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

import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/main_content.dart';
import 'package:bikebuds/privacy_util.dart';
import 'package:flutter/material.dart';

import 'pages/pages.dart';

class MainScreen extends StatefulWidget {
  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedDrawerItem = 1;

  @override
  Widget build(BuildContext context) {
    var firebase = FirebaseContainer.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text("Bikebuds"),
      ),
      drawer: buildDrawer(firebase),
      body: MainContent(_selectedDrawerItem),
    );
  }

  Drawer buildDrawer(FirebaseContainerState firebase) {
    List<Widget> children = [];
    children.add(DrawerHeader(child: Container()));
    for (int i = 0; i < pages.length; i++) {
      children.add(ListTile(
        title: Text(pages[i].title),
        onTap: () {
          setState(() {
            _selectedDrawerItem = i;
            Navigator.pop(context);
          });
        },
      ));
    }
    return Drawer(
      child: Column(
        children: <Widget>[
          Expanded(
            child: ListView(
              // Important: Remove any padding from the ListView.
              padding: EdgeInsets.zero,
              children: children,
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
}

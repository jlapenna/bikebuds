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
import 'package:bikebuds/main_content.dart';
import 'package:bikebuds/user_state.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:transparent_image/transparent_image.dart';
import 'package:url_launcher/url_launcher.dart';

import 'pages/pages.dart' as p;

class MainScreen extends StatefulWidget {
  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedDrawerItem = 0;

  @override
  Widget build(BuildContext context) {
    var userState = Provider.of<UserState>(context);
    var frontendUrl = Provider.of<Config>(context)?.config["devserver_url"];
    var pages = p.createPages(frontendUrl);
    return Scaffold(
      appBar: AppBar(
        title: Text("Bikebuds"),
      ),
      drawer: buildDrawer(pages, userState),
      body: MainContent(mainContentGlobalKey, pages, _selectedDrawerItem),
    );
  }

  Drawer buildDrawer(List<p.Page> pages, UserState userState) {
    var name = userState.displayName;
    var email = userState.email;
    var photoUrl = userState.photoUrl;
    var profilePhoto = photoUrl == null
        ? MemoryImage(
            kTransparentImage,
          )
        : NetworkImage(photoUrl);
    final List<Widget> children = [
      UserAccountsDrawerHeader(
          accountEmail: Text(email),
          accountName: Text(name),
          currentAccountPicture: CircleAvatar(
            backgroundImage: profilePhoto,
          ))
    ];
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
                    AboutListTile(
                      child: Center(
                        child: Text('ToS - Privacy'),
                      ),
                      aboutBoxChildren: <Widget>[
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
                    )
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

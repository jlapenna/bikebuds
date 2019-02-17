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

import 'dart:async';

import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/events_content.dart';
import 'package:bikebuds/privacy_util.dart';
import 'package:bikebuds/settings_content.dart';
import 'package:bikebuds/sign_in_screen.dart';
import 'package:flutter/material.dart';

class MainScreen extends StatefulWidget {
  final onSignedIn;

  MainScreen({Key key, this.onSignedIn}) : super(key: key);

  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedDrawerItem = 0;

  Future<FirebaseState> firebaseLoader;
  FirebaseState firebase;
  FirebaseSignInState signedInState;

  BikebudsState bikebuds;

  @override
  void initState() {
    super.initState();
    firebaseLoader = loadFirebase(context).then(_onLoaded);
  }

  FutureOr<FirebaseState> _onLoaded(FirebaseState firebase) async {
    print('Main._onLoaded');

    // Ensure we're signed in.
    FirebaseSignInState signedInState = await ensureSignedIn(context, firebase);
    print('Main._onLoaded: signedIn: ${signedInState?.signedIn}');
    if (signedInState == null || !signedInState.signedIn) {
      Navigator.pop(context);
      return firebase;
    }

    // Set up a bikebuds API client.
    var bikebuds;
    if (signedInState != null && signedInState.signedIn) {
      bikebuds = BikebudsState(Future(() async => firebase));
    }

    // Notify.
    setState(() {
      this.signedInState = signedInState;
      this.firebase = firebase;
      this.bikebuds = bikebuds;
    });

    // Notify our parent...
    widget.onSignedIn(firebase, bikebuds, signedInState);

    // Return a loaded firebase.
    return firebase;
  }

  @override
  Widget build(BuildContext context) {
    if (signedInState == null) {
      return Scaffold(
        appBar: AppBar(
          title: Text("Bikebuds"),
        ),
        body: Container(),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text("Bikebuds"),
      ),
      drawer: buildDrawer(),
      body: buildBody(),
    );
  }

  Drawer buildDrawer() {
    if (firebase == null || signedInState == null) {
      return null;
    }

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

  Widget buildBody() {
    if (firebase == null || signedInState == null) {
      return GestureDetector(
        child: Center(
          child: Text('ToS - Privacy'),
        ),
        onTap: () {
          Navigator.pop(context);
          showPrivacyDialog(context);
        },
      );
    }

    switch (_selectedDrawerItem) {
      case 0:
        return EventsContent(firebase: firebase);
      case 1:
        return SettingsContent(bikebuds: bikebuds);
      default:
        return Container();
    }
  }
}

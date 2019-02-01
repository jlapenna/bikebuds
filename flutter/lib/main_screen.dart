// Copyright 2015 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import 'dart:async';

import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds/firebase_http_client.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/home_content.dart';
import 'package:bikebuds/settings_content.dart';
import 'package:bikebuds/sign_in_screen.dart';
import 'package:bikebuds_api/bikebuds/v1.dart';
import 'package:firebase_auth/firebase_auth.dart';
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
  BikebudsState bikebuds;

  @override
  void initState() {
    super.initState();
    firebaseLoader = loadFirebase(context).then(_onLoaded);
    bikebuds = BikebudsState(firebaseLoader);
  }

  FutureOr<FirebaseState> _onLoaded(FirebaseState firebase) async {
    print('Main._onLoaded');

    // Ensure we're signed in.
    FirebaseSignInState signedInState = await ensureSignedIn(context, firebase);
    print('Main._onLoaded: signedIn: ${signedInState.signedIn}');

    // Notify our parent...
    widget.onSignedIn(firebase, bikebuds, signedInState);

    setState(() {
      this.firebase = firebase;
    });
    return firebase;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Bikebuds"),
      ),
      drawer: Drawer(
        child: ListView(
          // Important: Remove any padding from the ListView.
          padding: EdgeInsets.zero,
          children: buildDrawerItems(),
        ),
      ),
      body: buildBody(),
    );
  }

  buildDrawerItems() {
    if (firebase == null) {
      return <Widget>[];
    }

    return <Widget>[
      DrawerHeader(),
      ListTile(
        title: Text('Home'),
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
    ];
  }

  Widget buildBody() {
    if (firebase == null) {
      return buildSplashProgressScaffold();
    }

    switch (_selectedDrawerItem) {
      case 0:
        return HomeContent(firebase: firebase);
      case 1:
        return SettingsContent(bikebuds: bikebuds);
      default:
        return buildDefault();
    }
  }

  Widget buildDefault() {
    return Center(
      child: Column(
        children: <Widget>[
          Text(firebase.toString()),
          FutureBuilder(
              future: bikebuds.user,
              builder: (context, AsyncSnapshot<FirebaseUser> snapshot) =>
                  Text(snapshot.data?.displayName ?? "No name")),
        ],
      ),
    );
  }
}

Scaffold buildSplashProgressScaffold() {
  return new Scaffold(
    body: new Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        new Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[],
        ),
      ],
    ),
  );
}

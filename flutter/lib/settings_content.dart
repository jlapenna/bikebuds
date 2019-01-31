// Copyright 2015 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import 'package:bikebuds/bikebuds_util.dart';
import 'package:bikebuds/profile_card.dart';
import 'package:bikebuds_api/bikebuds/v1.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

class SettingsContent extends StatefulWidget {
  final BikebudsState bikebuds;

  SettingsContent({this.bikebuds});

  @override
  _SettingsContentState createState() => _SettingsContentState();
}

class _SettingsContentState extends State<SettingsContent> {
  Future<FirebaseUser> userLoader;
  Future<MainProfileResponse> profileLoader;

  @override
  initState() {
    super.initState();
    userLoader = widget.bikebuds.user;
    profileLoader = widget.bikebuds.profile;
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: new Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FutureBuilder(
              future: Future.wait([userLoader, profileLoader]),
              builder: (context, snapshot) {
                var user = snapshot.data == null ? null : snapshot.data[0];
                var profile = snapshot.data == null ? null : snapshot.data[1];
                return ProfileCard(user, profile);
              }),
        ],
      ),
    );
  }
}

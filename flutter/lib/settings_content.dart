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

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

import 'package:bikebuds_api/api.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:transparent_image/transparent_image.dart';

class ProfileCard extends StatelessWidget {
  final FirebaseUser firebaseUser;
  final Profile profile;
  final ClientStateEntity clientState;

  ProfileCard(this.firebaseUser, this.profile, [this.clientState]);

  @override
  Widget build(BuildContext context) {
    var photoUrl =
        profile?.athlete?.properties?.profileMedium ?? firebaseUser?.photoUrl;
    var profilePhoto = photoUrl == null
        ? MemoryImage(
            kTransparentImage,
          )
        : NetworkImage(photoUrl);
    var avatar = CircleAvatar(
      backgroundImage: profilePhoto,
      radius: 64,
    );
    var name = firebaseUser == null
        ? ""
        : firebaseUser?.displayName ?? firebaseUser?.email;

    var city = profile?.athlete?.properties?.city ?? "";

    var registered = clientState?.properties?.token == null ? "" : "Registered";
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            avatar,
            Text(name),
            Text(city),
            Text(registered),
            RaisedButton(onPressed: () {}, child: Text("Connect Services")),
          ],
        ),
      ),
    );
  }
}
/**
 * Copyright 2019 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import 'package:bikebuds_api/bikebuds/v1.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:transparent_image/transparent_image.dart';

class ProfileCard extends StatelessWidget {
  final FirebaseUser firebaseUser;
  final SharedDatastoreUsersClientMessage client;
  final MainProfileResponse profile;

  ProfileCard(this.firebaseUser, this.client, this.profile);

  @override
  Widget build(BuildContext context) {
    var profilePhoto = profile == null
        ? Image.memory(kTransparentImage)
        : FadeInImage.memoryNetwork(
            placeholder: kTransparentImage, image: profile?.athlete?.profile);
    String name = firebaseUser == null
        ? ""
        : (firebaseUser?.displayName ?? firebaseUser?.email);
    var registered =
        (client?.id != null) ? "Client registered" : "Not registered.";
    var city = profile?.athlete?.city ?? "Profile not available";
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        profilePhoto,
        Text(name),
        Text(city),
        Text(registered),
      ],
    );
  }
}
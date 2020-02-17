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

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../client_state_entity_state.dart';
import '../../user_state.dart';

class ProfileCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    var userState = Provider.of<UserState>(context);
    var profilePhoto = userState.profilePhoto;
    var avatar = CircleAvatar(backgroundImage: profilePhoto, radius: 64);

    var clientState = Provider.of<BikebudsClientState>(context);
    var registered =
        clientState?.client?.properties?.token == null ? "" : "Registered";

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            avatar,
            Text(userState.displayName),
            Text(userState.city),
            Text(registered),
            RaisedButton(onPressed: () {}, child: Text("Connect Services")),
          ],
        ),
      ),
    );
  }
}

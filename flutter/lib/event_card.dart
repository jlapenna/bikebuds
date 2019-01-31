// Copyright 2015 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import 'package:bikebuds/firebase_util.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
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

import 'package:flutter/material.dart';

class EventCard extends StatelessWidget {
  final FirebaseState firebase;
  final DocumentReference eventRef;
  final DocumentSnapshot event;

  EventCard({this.firebase, this.eventRef, this.event});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        event != null ? Text(event['title']) : Text("No event"),
        event != null
            ? Text(event['votes']?.toString() ?? "No votes")
            : Text("No event"),
        FloatingActionButton(
            child: Icon(Icons.add),
            onPressed: () {
              print('Eventcard: buttonPushed');
              firebase.firestore.runTransaction((Transaction tx) async {
                print('Eventcard: transaction executing');
                DocumentSnapshot postSnapshot = await tx.get(eventRef);
                if (postSnapshot.exists) {
                  await tx.update(eventRef, <String, dynamic>{
                    'votes': (postSnapshot.data['votes'] ?? 0) + 1
                  });
                }
              });
            }),
      ],
    );
  }
}

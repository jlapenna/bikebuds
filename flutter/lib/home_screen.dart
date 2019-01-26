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

import 'package:bikebuds/event_card.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/profile_card.dart';
import 'package:bikebuds_api/bikebuds/v1.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  final FirebaseState firebase;
  final FirebaseState firebaseNext;
  final BikebudsApi api;
  final SharedDatastoreUsersClientMessage client;
  final MainProfileResponse profile;

  HomeScreen(
      {Key key,
      @required this.firebase,
      @required this.firebaseNext,
      @required this.api,
      @required this.client,
      @required this.profile})
      : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Future<DocumentSnapshot> eventFuture;
  DocumentReference eventRef;

  @override
  void initState() {
    super.initState();

    var collection = widget.firebaseNext.firestore.collection("events");
    eventRef = collection.document("root-event");
    eventFuture = eventRef.get();
  }

  @override
  Widget build(BuildContext context) {
    var userFuture = widget.firebase.auth.currentUser();
    if (userFuture == null) {
      Navigator.pushNamed(context, "/signin");
    }

    return Scaffold(
      appBar: AppBar(
        title: Text("Bikebuds"),
      ),
      body: Center(
          child: Column(
        children: <Widget>[
          buildProfileCardBuilder(userFuture),
          buildEventCardBuilder()
        ],
      )),
    );
  }

  FutureBuilder<FirebaseUser> buildProfileCardBuilder(
      Future<FirebaseUser> userFuture) {
    return FutureBuilder(
        future: userFuture,
        builder: (context, snapshot) {
          return ProfileCard(snapshot.data, widget.client, widget.profile);
        });
  }

  StreamBuilder<DocumentSnapshot> buildEventCardBuilder() {
    return StreamBuilder<DocumentSnapshot>(
        stream: eventRef.snapshots(),
        builder:
            (BuildContext context, AsyncSnapshot<DocumentSnapshot> snapshot) {
          if (snapshot.hasError) return new Text('Error: ${snapshot.error}');
          switch (snapshot.connectionState) {
            case ConnectionState.waiting:
              return new Text('Loading...');
            default:
              return EventCard(widget.firebaseNext, eventRef, snapshot.data);
          }
        });
  }
}

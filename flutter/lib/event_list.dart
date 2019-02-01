// Copyright 2015 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import 'package:bikebuds/event_screen.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';

class EventList extends StatefulWidget {
  final FirebaseState firebase;

  EventList({this.firebase});

  @override
  _EventListState createState() => _EventListState();
}

class _EventListState extends State<EventList> {
  @override
  Widget build(BuildContext context) {
    return StreamBuilder<QuerySnapshot>(
        stream: widget.firebase.firestore.collection('events').snapshots(),
        builder: (BuildContext context, AsyncSnapshot<QuerySnapshot> snapshot) {
          return ListView(children: createChildren(snapshot));
        });
  }

  List<Widget> createChildren(AsyncSnapshot<QuerySnapshot> snapshot) {
    if (snapshot.data == null) {
      return List<Widget>();
    }
    return snapshot.data.documents
        .map(
          (document) => buildItem(document),
        )
        .toList();
  }

  Widget buildItem(DocumentSnapshot event) {
    return ListTile(
      title: Text(event['title']),
      subtitle: Text(
        event['start_date'].toString(),
      ),
      onTap: () {
        print('XXX: tapped : ${event.reference.snapshots()}');
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => EventScreen(
                firebase: widget.firebase,
                event: event),
          ),
        );
      },
    );
  }
}

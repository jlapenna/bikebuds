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

import 'package:bikebuds/firebase_util.dart';
import 'package:bikebuds/pages/events/event_page.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../date_util.dart';

class EventsList extends StatefulWidget {
  EventsList();

  @override
  _EventsListState createState() => _EventsListState();
}

class _EventsListState extends State<EventsList> {
  @override
  Widget build(BuildContext context) {
    var firebase = Provider.of<FirebaseState>(context);
    return StreamBuilder<QuerySnapshot>(
        stream: firebase.firestore.collection('events').snapshots(),
        builder: (BuildContext context, AsyncSnapshot<QuerySnapshot> snapshot) {
          switch (snapshot.connectionState) {
            case ConnectionState.waiting:
              return Center(child: new CircularProgressIndicator());
            default:
              return ListView(children: createChildren(snapshot));
          }
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
    var startDate = event.data()['start_date'] == null
        ? ""
        : dateTimeFormat.format(event.data()['start_date'].toDate());
    return ListTile(
      title: Text(event.data()['title']),
      subtitle: Text(startDate),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => EventPage(event: event),
          ),
        );
      },
    );
  }
}

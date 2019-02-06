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

import 'dart:async';

import 'package:bikebuds/firebase_util.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

class EventScreen extends StatefulWidget {
  final FirebaseState firebase;
  final DocumentSnapshot event;

  EventScreen({this.firebase, this.event});

  @override
  _EventScreenState createState() => _EventScreenState();
}

class _EventScreenState extends State<EventScreen> {
  Stream<DocumentSnapshot> eventStream;
  StreamSubscription<DocumentSnapshot> eventStreamSubscription;

  FocusNode titleFocusNode;
  TextEditingController titleController;

  FocusNode descriptionFocusNode;
  TextEditingController descriptionController;

  Map<String, dynamic> latestEvent;

  @override
  void initState() {
    super.initState();
    // TODO: This doesn't handle the screen being background.
    // TODO: We overwrite any remote updates when when description focus changes.

    titleFocusNode = FocusNode();
    titleFocusNode.addListener(titleFocusListener);
    titleController = new TextEditingController(text: widget.event['title']);

    descriptionFocusNode = FocusNode();
    descriptionFocusNode.addListener(descriptionFocusListener);
    descriptionController =
        new TextEditingController(text: widget.event['description']);

    eventStream = widget.event.reference.snapshots();
    eventStreamSubscription = eventStream.listen(eventStreamListener);
  }

  void titleFocusListener() {
    print('EventScreen.titleFocusListener: Focus: ${titleFocusNode.hasFocus}');
    if (!titleFocusNode.hasFocus) {
      // We lost focus.
      widget.firebase.firestore.runTransaction((Transaction tx) async {
        print(
            'EventScreen.titleFocusListener: running transaction "${titleController.text}"');
        await tx.update(widget.event.reference, <String, dynamic>{
          'title': titleController.text,
        });
        print('EventScreen.titleFocusListener: completed transaction.');
      });
    }
  }

  void descriptionFocusListener() {
    print(
        'EventScreen.descriptionFocusListener: Focus: ${descriptionFocusNode.hasFocus}');
    if (!descriptionFocusNode.hasFocus) {
      // We lost focus.
      widget.firebase.firestore.runTransaction((Transaction tx) async {
        print(
            'EventScreen.descriptionFocusListener: running transaction "${descriptionController.text}"');
        await tx.update(widget.event.reference, <String, dynamic>{
          'description': descriptionController.text,
        });
        print('EventScreen.descriptionFocusListener: completed transaction.');
      });
    }
  }

  /// Updates this screen with the latest changes from firebase.
  void eventStreamListener(latestSnapshot) {
    // Only update the UI from firebase if those elements are not focused.
    if (!titleFocusNode.hasFocus) {
      titleController.text = latestSnapshot['title'];
    }
    if (!descriptionFocusNode.hasFocus) {
      descriptionController.text = latestSnapshot['description'];
    }
    setState(() {
      this.latestEvent = latestSnapshot.data;
    });
  }

  @override
  void dispose() {
    titleFocusNode?.dispose();
    titleController?.dispose();

    descriptionFocusNode?.dispose();
    descriptionController?.dispose();

    eventStreamSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Ride"),
      ),
      body: buildBody(),
    );
  }

  Widget buildBody() {
    return ListView(
      children: <Widget>[
        StreamBuilder(
          stream: eventStream,
          builder:
              (BuildContext context, AsyncSnapshot<DocumentSnapshot> snapshot) {
            switch (snapshot.connectionState) {
              case ConnectionState.waiting:
                return Center(child: new CircularProgressIndicator());
              default:
                return buildEvent(snapshot);
            }
          },
        ),
      ],
    );
  }

  Widget buildEvent(AsyncSnapshot<DocumentSnapshot> snapshot) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            TextField(
              controller: titleController,
              focusNode: titleFocusNode,
              autocorrect: true,
              maxLines: 1,
              textCapitalization: TextCapitalization.sentences,
              decoration: InputDecoration(labelText: 'Title'),
              style: Theme.of(context).textTheme.headline,
            ),
            TextField(
              controller: descriptionController,
              focusNode: descriptionFocusNode,
              autocorrect: true,
              maxLines: 4,
              textCapitalization: TextCapitalization.sentences,
              decoration: InputDecoration(labelText: 'Description'),
              style: Theme.of(context).textTheme.body1,
            ),
          ],
        ),
      ),
    );
  }
}

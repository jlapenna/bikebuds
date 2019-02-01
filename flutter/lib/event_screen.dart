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

import 'package:bikebuds/firebase_util.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter/material.dart';

class EventScreen extends StatefulWidget {
  final FirebaseState firebase;
  final DocumentSnapshot event;

  EventScreen({this.firebase, this.event});

  @override
  _EventScreenState createState() => _EventScreenState();
}

class _EventScreenState extends State<EventScreen> {
  Stream<DocumentSnapshot> _eventStream;
  TextEditingController _titleController;
  Map<String, dynamic> event;

  @override
  void initState() {
    super.initState();
    _eventStream = widget.event.reference.snapshots();
    _eventStream.listen((event) {
      // This loop-back allows text updates from other devices to immediately
      // cause a local update.
      _titleController.text = event['title'];
      setState(() {
        this.event = event.data;
      });
    });

    _titleController = new TextEditingController(text: widget.event['title']);
    _titleController.addListener(_titleListener);
  }

  void _titleListener() async {
    if (event != null && event['title'] == _titleController.text) {
      // Debounce events, we are notified even when selection criteria changes!
      return;
    }
    print(
        '_titleListener: starting transaction ${_titleController.text}, ${event}');
    widget.firebase.firestore.runTransaction((Transaction tx) async {
      print('_titleListener: running transaction ${_titleController.text}');
      await tx.update(widget.event.reference, <String, dynamic>{
        'title': _titleController.text,
      });
      print('_titleListener: completed transaction.');
    });
  }

  @override
  void dispose() {
    _titleController?.dispose();
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
          stream: _eventStream,
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
              controller: _titleController,
              autocorrect: true,
              maxLines: 1,
              textCapitalization: TextCapitalization.sentences,
              decoration: InputDecoration(labelText: 'Title'),
              style: Theme.of(context).textTheme.headline,
            ),
          ],
        ),
      ),
    );
  }
}

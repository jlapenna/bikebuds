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

import 'dart:async';

import 'package:bikebuds/date_util.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:datetime_picker_formfield/datetime_picker_formfield.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:provider/provider.dart';

class EventPage extends StatefulWidget {
  final DocumentSnapshot event;

  EventPage({this.event});

  @override
  _EventPageState createState() => _EventPageState();
}

class _EventPageState extends State<EventPage> {
  FirebaseState firebase;

  DocumentSnapshot event;

  Stream<DocumentSnapshot> eventStream;
  StreamSubscription<DocumentSnapshot> eventStreamSubscription;

  FocusNode titleFocusNode;
  TextEditingController titleController;

  FocusNode descriptionFocusNode;
  TextEditingController descriptionController;

  @override
  void initState() {
    super.initState();
    // TODO: This doesn't handle the screen being background.
    // TODO: We overwrite any remote updates when when description focus changes.

    this.event = widget.event;

    titleFocusNode = FocusNode();
    titleFocusNode.addListener(titleFocusListener);
    titleController =
        new TextEditingController(text: widget.event.data()['title']);

    descriptionFocusNode = FocusNode();
    descriptionFocusNode.addListener(descriptionFocusListener);
    descriptionController =
        new TextEditingController(text: widget.event.data()['description']);

    eventStream = widget.event.reference.snapshots();
    eventStreamSubscription = eventStream.listen(eventStreamListener);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    this.firebase = Provider.of<FirebaseState>(context);
  }

  void titleFocusListener() {
    print('EventScreen.titleFocusListener: Focus: ${titleFocusNode.hasFocus}');
    if (!titleFocusNode.hasFocus) {
      // We lost focus.
      firebase.firestore.runTransaction((Transaction tx) async {
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
      firebase.firestore.runTransaction((Transaction tx) async {
        print(
            'EventScreen.descriptionFocusListener: running transaction "${descriptionController.text}"');
        await tx.update(widget.event.reference, <String, dynamic>{
          'description': descriptionController.text,
        });
        print('EventScreen.descriptionFocusListener: completed transaction.');
      });
    }
  }

  // Updates this screen with the latest changes from firebase.
  void eventStreamListener(latestSnapshot) {
    // Only update the UI from firebase if those elements are not focused.
    if (!titleFocusNode.hasFocus) {
      titleController.text = latestSnapshot['title'];
    }
    if (!descriptionFocusNode.hasFocus) {
      descriptionController.text = latestSnapshot['description'];
    }
    // TODO: Update start date with remote changes.

    setState(() {
      this.event = latestSnapshot;
    });
  }

  void handleStartDateChanged(newStartDate) {
    print('EventScreen.handleStartDateChanged: $newStartDate');
    firebase.firestore.runTransaction((Transaction tx) async {
      print(
          'EventScreen.handleStartDateChanged: running transaction "$newStartDate"');
      var startDate =
          newStartDate != null ? Timestamp.fromDate(newStartDate) : null;
      await tx.update(widget.event.reference, <String, dynamic>{
        'start_date': startDate,
      });
      print('EventScreen.handleStartDateChanged: completed transaction.');
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
    DateTime startDate = widget.event.data()['start_date']?.toDate();
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
              style: Theme.of(context).textTheme.headline5,
              decoration: InputDecoration(
                  labelText: 'Title',
                  floatingLabelBehavior: FloatingLabelBehavior.never),
            ),
            DateTimeField(
                format: dateTimeFormat,
                initialValue: startDate,
                onChanged: handleStartDateChanged,
                decoration: InputDecoration(labelText: 'Start Date'),
                onShowPicker: (context, currentValue) async {
                  final date = await showDatePicker(
                    context: context,
                    firstDate: DateTime(2018),
                    initialDate: startDate ?? DateTime.now(),
                    lastDate: DateTime(2025),
                  );
                  if (date != null) {
                    final time = await showTimePicker(
                      context: context,
                      initialTime:
                          TimeOfDay.fromDateTime(startDate ?? DateTime.now()),
                    );
                    return DateTimeField.combine(date, time);
                  }
                  return currentValue;
                }),
            TextField(
              controller: descriptionController,
              focusNode: descriptionFocusNode,
              autocorrect: true,
              maxLines: 4,
              textCapitalization: TextCapitalization.sentences,
              style: Theme.of(context).textTheme.bodyText2,
              decoration: InputDecoration(labelText: 'Description'),
            ),
          ],
        ),
      ),
    );
  }
}

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

import 'package:bikebuds/events_list.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:flutter/material.dart';

class EventsContent extends StatefulWidget {
  final FirebaseState firebase;

  EventsContent({this.firebase});

  @override
  _EventsContentState createState() => _EventsContentState();
}

class _EventsContentState extends State<EventsContent> {
  @override
  Widget build(BuildContext context) {
    return Container(
      child: EventsList(firebase: widget.firebase),
    );
  }
}

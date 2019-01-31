// Copyright 2015 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import 'package:bikebuds/event_list.dart';
import 'package:bikebuds/firebase_util.dart';
import 'package:flutter/material.dart';

class HomeContent extends StatefulWidget {
  final FirebaseState firebase;

  HomeContent({this.firebase});

  @override
  _HomeContentState createState() => _HomeContentState();
}

class _HomeContentState extends State<HomeContent> {
  @override
  Widget build(BuildContext context) {
    return Container(
      child: EventList(firebase: widget.firebase),
    );
  }
}

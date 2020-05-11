// Copyright 2020 Google Inc. All Rights Reserved.
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

import 'dart:isolate';

import 'package:bikebuds/app.dart';
import 'package:bikebuds/main_content.dart';
import 'package:bikebuds/pages/measures/measures_state.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

registerFirebaseMessaging() {
  print(
      'FirebaseMessaging: configuring in Isolate#${shortHash(Isolate.current)}');
  try {
    FirebaseMessaging().requestNotificationPermissions();
    return FirebaseMessaging()
      ..configure(
          onBackgroundMessage: onMessage,
          onMessage: onMessage,
          onLaunch: onLaunch,
          onResume: onResume);
  } catch (err) {
    print('FirebaseMessaging: configure failed: $err');
  }
}

Future<dynamic> onResume(Map<String, dynamic> message) async {
  print(
      'FirebaseMessaging.onResume: $message in Isolate#${shortHash(Isolate.current)}');
}

Future<dynamic> onLaunch(Map<String, dynamic> message) async {
  print(
      'FirebaseMessaging.onLaunch: $message in Isolate#${shortHash(Isolate.current)}');
}

Future onMessage(Map<String, dynamic> message) async {
  print(
      'FirebaseMessaging.onMessage: $message in Isolate#${shortHash(Isolate.current)}');
  handleData(message);
  handleNotification(message);
  return Future.value(message);
}

void handleNotification(Map<String, dynamic> message) {
  var currentContext = mainContentGlobalKey.currentContext;
  if (currentContext == null) {
    print('FirebaseMessaging.handleNotification: No context, aborting');
    return;
  }
  if (message.containsKey('notification') &&
      message['notification'].containsKey('title') &&
      (message['notification']['title'] as String).isNotEmpty &&
      message['notification'].containsKey('body') &&
      (message['notification']['body'] as String).isNotEmpty) {
    Scaffold.of(currentContext).showSnackBar(
      SnackBar(
        content: ListTile(
          title: Text(message['notification']['title']),
          subtitle: Text(message['notification']['body']),
        ),
      ),
    );
  }
}

Future handleData(Map<String, dynamic> message) async {
  var currentContext = appDelegateGlobalKey.currentContext;
  if (currentContext == null) {
    print('FirebaseMessaging.handleData: No context, aborting');
    return;
  }
  if (message.containsKey('data') && message['data'].containsKey('refresh')) {
    print(
        'FirebaseMessaging.handleData: Refresh: ${message['data']['refresh']}');
    switch (message['data']['refresh']) {
      case 'weight':
        try {
          await Provider.of<MeasuresState>(currentContext, listen: false)
              .refresh();
          print('FirebaseMessaging.handleData: Refreshed weight');
        } catch (err, stack) {
          print('FirebaseMessaging.handleData: Refresh failed: $err, $stack');
        }
        break;
      default:
        print('FirebaseMessaging.handleData: Unrecognized refresh');
    }
  }
}

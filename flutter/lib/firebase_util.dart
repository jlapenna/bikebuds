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

import 'dart:convert';

import 'package:bikebuds/config.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/widgets.dart';

class FirebaseSignInState {
  final FirebaseUser user;
  final FirebaseUser userNext;

  FirebaseSignInState(this.user, this.userNext);

  @override
  String toString() {
    return 'FirebaseUsers(${user?.uid}, ${userNext?.uid})';
  }

  get signedIn => user != null && userNext != null;
}

class FirebaseContainer extends StatefulWidget {
  final Widget child;

  FirebaseContainer({@required this.child});

  static FirebaseContainerState of(BuildContext context) {
    return (context.inheritFromWidgetOfExactType(_InheritedFirebaseContainer)
            as _InheritedFirebaseContainer)
        .data;
  }

  @override
  FirebaseContainerState createState() => new FirebaseContainerState();
}

class FirebaseContainerState extends State<FirebaseContainer> {
  bool _loading = false;

  final FirebaseApp app = FirebaseApp.instance;
  final FirebaseAuth auth = FirebaseAuth.instance;
  final FirebaseMessaging messaging = FirebaseMessaging();

  FirebaseApp appNext;
  FirebaseAuth authNext;
  Firestore firestore;

  @override
  void didChangeDependencies() {
    var config = ConfigContainer.of(context);
    if (!_loading && config != null) {
      _loadFirebase();
    }
    super.didChangeDependencies();
  }

  _loadFirebase() async {
    print('FirebaseContainerState._loadFirebase');
    _loading = true;
    var loadedJson = await json.decode(await DefaultAssetBundle.of(context)
        .loadString("android/app/google-services-next-android.json"));
    FirebaseOptions options = _toFirebaseOptions(loadedJson);
    var appNext = await _loadAppNext(options);
    var authNext = FirebaseAuth.fromApp(appNext);
    var firestore = Firestore(app: appNext);
    setState(() {
      this.appNext = appNext;
      this.authNext = authNext;
      this.firestore = firestore;
    });
  }

  FirebaseOptions _toFirebaseOptions(dynamic config) {
    // https://firebase.google.com/docs/reference/swift/firebasecore/api/reference/Classes/FirebaseOptions
    return FirebaseOptions(
        googleAppID: config['client'][0]['client_info']['mobilesdk_app_id'],
        apiKey: config['client'][0]['api_key'][0]
            ['current_key'], // iOS API Key?
        bundleID: "bikebuds.cc", // iOS Bundle ID
        clientID: null, // iOS Client ID
        trackingID: null, // Analytics Tracking ID
        gcmSenderID: config['project_info']['project_number'],
        projectID: config['project_info']['project_id'],
        androidClientID: config['client'][0]['oauth_client'][0]['client_id'],
        databaseURL: config['project_info']['firebase_url'],
        deepLinkURLScheme: null, // Durable Deep Link service
        storageBucket: config['project_info']['storage_bucket']);
  }

  Future<FirebaseApp> _loadAppNext(FirebaseOptions options) async {
    try {
      return await FirebaseApp.configure(name: "next", options: options);
    } catch (e) {
      return await FirebaseApp.appNamed("next");
    }
  }

  @override
  Widget build(BuildContext context) {
    return new _InheritedFirebaseContainer(
      data: this,
      child: widget.child,
    );
  }
}

class _InheritedFirebaseContainer extends InheritedWidget {
  // Data is your entire state. In our case just 'User'
  final FirebaseContainerState data;

  // You must pass through a child and your state.
  const _InheritedFirebaseContainer({
    Key key,
    @required this.data,
    @required Widget child,
  }) : super(key: key, child: child);

  // This is a built in method which you can use to check if
  // any state has changed. If not, no reason to rebuild all the widgets
  // that rely on your state.
  @override
  bool updateShouldNotify(_InheritedFirebaseContainer old) => true;
}

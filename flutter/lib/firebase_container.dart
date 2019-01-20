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
import 'package:flutter/widgets.dart';

class FirebaseContainer extends StatefulWidget {
  final Widget child;
  final FirebaseState firebase;
  final Future<FirebaseState> firebaseNextLoader;

  FirebaseContainer(
      {@required this.child,
      @required this.firebase,
      @required this.firebaseNextLoader});

  static FirebaseContainerState of(BuildContext context) {
    return (context.inheritFromWidgetOfExactType(_InheritedFirebaseContainer)
            as _InheritedFirebaseContainer)
        .state;
  }

  @override
  FirebaseContainerState createState() =>
      new FirebaseContainerState(firebase, firebaseNextLoader);
}

class FirebaseContainerState extends State<FirebaseContainer> {
  final FirebaseState firebase;
  final Future<FirebaseState> _firebaseNextLoader;
  FirebaseState firebaseNext;

  FirebaseContainerState(this.firebase, this._firebaseNextLoader);

  @override
  void initState() {
    super.initState();
    loadFirebaseNext();
  }

  void loadFirebaseNext() async {
    var firebaseNext = await _firebaseNextLoader;
    setState(() {
      this.firebaseNext = firebaseNext;
    });
  }

  @override
  Widget build(BuildContext context) {
    return new _InheritedFirebaseContainer(
      state: this,
      child: widget.child,
    );
  }
}

class _InheritedFirebaseContainer extends InheritedWidget {
  final FirebaseContainerState state;

  _InheritedFirebaseContainer({
    Key key,
    this.state,
    @required Widget child,
  }) : super(key: key, child: child);

  @override
  bool updateShouldNotify(_InheritedFirebaseContainer old) =>
      old.state != this.state;
}

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

import 'package:firebase_auth/firebase_auth.dart';

class FirebaseUserWrapper {
  final FirebaseUser _firebaseUser;

  factory FirebaseUserWrapper(FirebaseUser firebaseUser) {
    if (firebaseUser == null) {
      return null;
    }
    return FirebaseUserWrapper._internal(firebaseUser);
  }

  FirebaseUserWrapper._internal(this._firebaseUser) {
    if (_firebaseUser is! FirebaseUser) throw new ArgumentError(_firebaseUser);
  }

  get uid => _firebaseUser?.uid;
  get displayName => _firebaseUser?.displayName;
  get email => _firebaseUser?.email;
  get photoUrl => _firebaseUser?.photoUrl;

  Future<String> getAccessToken({bool refresh: false}) {
    return _firebaseUser
        .getIdToken(refresh: refresh)
        .then((IdTokenResult idToken) => idToken.token);
  }
}

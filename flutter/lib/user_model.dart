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

import 'package:bikebuds_api/api.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/widgets.dart';
import 'package:scoped_model/scoped_model.dart';

class UserModel extends Model {
  Profile _profile;
  FirebaseUser _firebaseUser;

  Profile get profile => _profile;
  FirebaseUser get firebaseUser => _firebaseUser;

  void updateProfile(FutureOr<Profile> response) async {
    _profile = await response;

    notifyListeners();
  }

  void updateUser(FutureOr<FirebaseUser> user) async {
    _firebaseUser = await user;

    notifyListeners();
  }

  static UserModel of(BuildContext context) =>
      ScopedModel.of<UserModel>(context);
}

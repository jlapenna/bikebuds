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

import 'package:bikebuds/firebase_user_wrapper.dart';
import 'package:bikebuds_api/api.dart' hide User;
import 'package:flutter/widgets.dart';
import 'package:transparent_image/transparent_image.dart';

class UserState with ChangeNotifier {
  FirebaseUserWrapper _user;
  Profile _profile;

  get displayName => _user?.displayName ?? _user?.email ?? "";
  get email => _user?.email ?? "";
  get photoUrl =>
      _profile?.athlete?.properties?.profileMedium ?? _user?.photoUrl;
  get profilePhoto => this.photoUrl == null
      ? MemoryImage(kTransparentImage)
      : NetworkImage(photoUrl);
  get city => _profile?.athlete?.properties?.city ?? "";

  set user(FirebaseUserWrapper value) {
    _user = value;
    notifyListeners();
  }

  set profile(Profile value) {
    _profile = value;
    notifyListeners();
  }
}

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

import 'package:bikebuds/profile_card.dart';
import 'package:bikebuds_api/api.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'bikebuds_api_testutil.dart';
import 'firebase_testutil.dart';

void main() {
  testWidgets('profile card smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.

    FirebaseUserMock mockFirebaseUser = newFirebaseUserMock();
    Profile fakeUser = newProfile();

    await tester.pumpWidget(
      MaterialApp(
        home: ProfileCard(mockFirebaseUser, fakeUser),
      ),
    );

    expect(find.text('Test Name'), findsOneWidget);

    expect(find.text('San Francisco'), findsOneWidget);
  });
}

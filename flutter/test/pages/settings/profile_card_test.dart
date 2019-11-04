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

import 'package:bikebuds/client_state_entity_state.dart';
import 'package:bikebuds/pages/settings/profile_card.dart';
import 'package:bikebuds/user_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import '../../bikebuds_api_testutil.dart';
import '../../firebase_testutil.dart';

void main() {
  testWidgets('profile card smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.

    var userState = UserState();
    userState.firebaseUser = newFirebaseUserMock();
    userState.profile = newProfileFake();

    await tester.pumpWidget(
      MaterialApp(
        home: MultiProvider(
          providers: [
            ChangeNotifierProvider.value(value: ClientStateEntityState()),
            ChangeNotifierProvider.value(value: userState),
          ],
          child: ProfileCard(),
        ),
      ),
    );

    expect(find.text('Test Name'), findsOneWidget);

    expect(find.text('San Francisco'), findsOneWidget);
  });
}

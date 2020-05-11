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

import 'package:bikebuds/bikebuds_api_state.dart';
import 'package:bikebuds/fake_user_wrapper.dart';
import 'package:bikebuds/pages/measures/measures_chart.dart';
import 'package:bikebuds/pages/measures/measures_state.dart';
import 'package:bikebuds/storage/entity_storage.dart';
import 'package:bikebuds/storage/storage.dart';
import 'package:bikebuds/user_state.dart';
import 'package:bikebuds_api/api.dart' hide UserState;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:sembast/sembast_memory.dart';

import '../../bikebuds_api_testutil.dart';

void main() {
  testWidgets('measures chart smoke test', (WidgetTester tester) async {
    var series = SeriesEntity()..key = defaultKey;
    series.properties = Series();
    series.properties.measures = [
      Measure.fromJson({
        'date': DateTime(2017, 9, 19, 11, 22, 33).toIso8601String(),
        'weight': 10
      }),
      Measure.fromJson({
        'date': DateTime(2017, 9, 26, 09, 11, 44).toIso8601String(),
        'weight': 20
      }),
      Measure.fromJson({
        'date': DateTime(2017, 10, 3, 01, 31, 30).toIso8601String(),
        'weight': 30
      }),
      Measure.fromJson({
        'date': DateTime(2017, 10, 10, 16, 33, 18).toIso8601String(),
        'weight': 40
      }),
    ];

    var db = await databaseFactoryMemory.openDatabase("path.db");
    Storage storage = Storage(db);
    // Not sure why sembast relies on a timeout to do work that we
    // can't get access to, to advance.
    // Could probably preload this, though to work around it:
    // https://github.com/tekartik/sembast.dart/blob/master/sembast/doc/open.md#preloading-data
    var putResult = storage.seriesStore.put(series);
    await tester.pump(new Duration(milliseconds: 500));
    await putResult;

    var userState = UserState();
    userState.user = FakeUserWrapper(displayName: "Test Name");
    userState.profile = newProfileFake();

    MeasuresState measuresState = MeasuresState(filter: 'weight')
      ..bikebudsApiState = BikebudsApiState()
      ..userState = userState
      ..storage = storage;

    await tester.pumpWidget(
      MaterialApp(
        home: MultiProvider(
          providers: [
            ChangeNotifierProvider.value(value: measuresState),
          ],
          child: MeasuresChart(),
        ),
      ),
    );
//    await tester.pump(new Duration(milliseconds: 500));
    await tester.pumpAndSettle();
    await storage.close();
  });
}

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

import 'package:bikebuds/pages/measures/measures_chart.dart';
import 'package:bikebuds/pages/measures/measures_state.dart';
import 'package:bikebuds_api/api.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

void main() {
  testWidgets('measures chart smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.

    MeasuresState measuresState = MeasuresState(filter: 'weight');
    measuresState.series = SeriesEntity();
    measuresState.series.properties = Series();
    measuresState.series.properties.measures = [
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
  });
}

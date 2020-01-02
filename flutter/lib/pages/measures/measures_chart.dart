// copyright 2019 google inc. all rights reserved.
//
// licensed under the apache license, version 2.0 (the "license");
// you may not use this file except in compliance with the license.
// you may obtain a copy of the license at
//
//     http://www.apache.org/licenses/license-2.0
//
// unless required by applicable law or agreed to in writing, software
// distributed under the license is distributed on an "as is" basis,
// without warranties or conditions of any kind, either express or implied.
// see the license for the specific language governing permissions and
// limitations under the license.

import 'package:bikebuds/app.dart';
import "package:bikebuds_api/api.dart";
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'measures_state.dart';

class MeasuresChart extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    var measuresState = Provider.of<MeasuresState>(context);
    print(
        'MeasuresChart: build: measures.length: ${measuresState.series?.measures?.length}');
    return new charts.TimeSeriesChart(
      _toSeriesList(measuresState.series),
      dateTimeFactory: const charts.UTCDateTimeFactory(),
    );
  }

  List<charts.Series<Measure, DateTime>> _toSeriesList(Series series) {
    return [
      new charts.Series<Measure, DateTime>(
        id: 'Measures',
        displayName: 'Measures',
        colorFn: (_, __) => charts.ColorUtil.fromDartColor(ACCENT_COLOR),
        domainFn: (Measure measure, _) => measure.date,
        measureFn: (Measure measure, _) => measure.weight,
        data: series?.measures ?? [],
      )
    ];
  }

  /// Create one series with sample hard coded data.
  static Series _createSampleData() {
    var series = Series();
    series.measures = [
      Measure.fromJson(
          {'date': DateTime(2017, 9, 19).toIso8601String(), 'weight': 10}),
      Measure.fromJson(
          {'date': DateTime(2017, 9, 26).toIso8601String(), 'weight': 20}),
      Measure.fromJson(
          {'date': DateTime(2017, 10, 3).toIso8601String(), 'weight': 30}),
      Measure.fromJson(
          {'date': DateTime(2017, 10, 10).toIso8601String(), 'weight': 40}),
    ];
    return series;
  }
}

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

import 'dart:math';

import 'package:bikebuds/app.dart';
import 'package:bikebuds/pages/measures/measures_state.dart';
import "package:bikebuds_api/api.dart" hide UserState;
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/material.dart';
import 'package:jiffy/jiffy.dart';
import 'package:provider/provider.dart';

enum Interval {
  DAY,
  WEEK,
  MONTH,
}

class MeasuresChart extends StatefulWidget {
  final int intervalCount;
  final int intervalStep;
  final Interval intervalUnit;

  MeasuresChart({
    this.intervalCount: 48,
    this.intervalStep: 1,
    this.intervalUnit: Interval.MONTH,
  });

  @override
  _MeasuresChartState createState() => _MeasuresChartState();
}

class _MeasuresChartState extends State<MeasuresChart> {
  Series series;
  List<Map<dynamic, dynamic>> measures = [];
  bool showFatLine;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    var measuresState = Provider.of<MeasuresState>(context);
    if (measuresState.series != series) {
      series = measuresState.series;
      handleMeasures(measuresState.series?.measures ?? []);
    }
  }

  handleMeasures(List<Measure> newMeasures) {
    DateTime preferredNextDate = Jiffy(DateTime.now().toUtc()).endOf('day');
    var earliestDate =
        _preferredNextDate(preferredNextDate, count: widget.intervalCount);
    List<Map<dynamic, dynamic>> measures = [];
    showFatLine = false;
    List<Measure> intervalMeasures = [];
    for (var i = newMeasures.length; i > 0; i--) {
      var measure = newMeasures[i - 1];
      if (measure.date.isBefore(earliestDate)) {
        // If the measure is out of bounds of our range, we're done.
        break;
      }
      if (measure.date.isBefore(preferredNextDate)) {
        // If the measure is a new interval, process the previous...
        Map<dynamic, dynamic> newMeasure =
            _processIntervalMeasures(preferredNextDate, intervalMeasures);
        if (newMeasure != null) {
          if (newMeasure.containsKey('fatRatio')) {
            showFatLine = true;
          }
          measures.insert(0, newMeasure);
        }

        // And start the next batch...
        preferredNextDate = _preferredNextDate(preferredNextDate);
        intervalMeasures = [];
      }
      intervalMeasures.insert(0, measure);
    }
    this.measures = measures;
  }

  @override
  Widget build(BuildContext context) {
    return charts.TimeSeriesChart(
      [
        charts.Series<Map<dynamic, dynamic>, DateTime>(
          id: 'Measures',
          displayName: 'Measures',
          colorFn: (_, __) => charts.ColorUtil.fromDartColor(ACCENT_COLOR),
          domainFn: (dynamic measure, _) => measure['date'],
          measureFn: (dynamic measure, _) => measure['weightAvg'],
          data: measures,
        ),
      ],
      animate: false,
      dateTimeFactory: const charts.LocalDateTimeFactory(),
      domainAxis: charts.DateTimeAxisSpec(
        tickFormatterSpec: charts.AutoDateTimeTickFormatterSpec(
          day: charts.TimeFormatterSpec(
              format: timeFormat(), transitionFormat: timeTransitionFormat()),
        ),
      ),
    );
  }

  timeFormat() {
    switch (widget.intervalUnit) {
      case Interval.DAY:
        return 'dd';
      case Interval.WEEK:
        return "dd'MM";
      case Interval.MONTH:
        return 'MM';
    }
  }

  timeTransitionFormat() {
    switch (widget.intervalUnit) {
      case Interval.DAY:
        return 'dd';
      case Interval.WEEK:
        return "dd'MM";
      case Interval.MONTH:
        return 'MM/dd/yyyy';
    }
  }

  _preferredNextDate(DateTime preferredNextDate, {int count: 1}) {
    switch (widget.intervalUnit) {
      case Interval.DAY:
        Jiffy j = Jiffy(preferredNextDate)
          ..subtract(days: widget.intervalStep * count)
          ..startOf('day');
        return j.utc();
      case Interval.WEEK:
        Jiffy j = Jiffy(preferredNextDate)
          ..subtract(weeks: widget.intervalStep * count)
          ..startOf('day');
        return j.utc();
      case Interval.MONTH:
        Jiffy j = Jiffy(preferredNextDate)
          ..subtract(months: widget.intervalStep * count)
          ..startOf('day');
        return j.utc();
    }
    return null;
  }

  static Map _processIntervalMeasures(
      DateTime preferredNextDate, List<Measure> intervalMeasures) {
    num weightSum = 0;
    num weightCount = 0;
    num weightMax = -1;
    num weightMin = double.maxFinite;
    num fatSum = 0;
    num fatCount = 0;
    for (Measure intervalMeasure in intervalMeasures) {
      num weight = intervalMeasure.weight;
      if (weight != null) {
        weightSum += weight;
        weightCount += 1;
        weightMax = max(weight, weightMax);
        weightMin = min(weight, weightMin);
      }
      if (intervalMeasure.fatRatio != null) {
        fatSum += intervalMeasure.fatRatio;
        fatCount += 1;
      }
    }
    if (weightCount > 0) {
      var weightAvg = weightSum / weightCount;
      Map<dynamic, dynamic> newMeasure = {
        'date': preferredNextDate,
        'weightAvg': weightAvg,
        'weightError': [weightAvg - weightMin, weightMax - weightAvg],
      };
      if (fatCount > 0) {
        newMeasure['fatRatio'] = fatSum / fatCount;
      }
      return newMeasure;
    }
    return null;
  }
}

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
import 'package:bikebuds_api/api.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:jiffy/jiffy.dart';
import 'package:provider/provider.dart';

DateFormat yMdFormat = new DateFormat.yMd();

enum Interval {
  DAY,
  WEEK,
  MONTH,
}

class MeasuresChart extends StatefulWidget {
  final String title;
  final int intervalCount;
  final int intervalStep;
  final Interval intervalUnit;

  MeasuresChart({
    this.title: "Monthly",
    this.intervalCount: 48,
    this.intervalStep: 1,
    this.intervalUnit: Interval.MONTH,
  });

  @override
  _MeasuresChartState createState() => _MeasuresChartState();
}

class _MeasuresChartState extends State<MeasuresChart> {
  SeriesEntity series;
  List<Measure> measures = [];
  bool showFatLine;

  DateTime _selectedDate;
  num _selectedWeight;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    var measuresState = Provider.of<MeasuresState>(context);
    if (measuresState.series != series) {
      series = measuresState.series;
      handleMeasures(measuresState.series?.properties?.measures ?? []);
    }
  }

  handleMeasures(List<Measure> newMeasures) {
    DateTime preferredNextDate = Jiffy(DateTime.now().toUtc()).endOf(Units.DAY);
    var earliestDate =
        _preferredNextDate(preferredNextDate, count: widget.intervalCount);
    List<Measure> measures = [];
    var showFatLine = false;
    List<Measure> intervalMeasures = [];
    for (var i = newMeasures.length; i > 0; i--) {
      var measure = newMeasures[i - 1];
      if (measure.date.isBefore(earliestDate)) {
        // If the measure is out of bounds of our range, we're done.
        break;
      }
      if (measure.date.isBefore(preferredNextDate)) {
        // If the measure is a new interval, process the previous...
        Measure newMeasure =
            _processIntervalMeasures(preferredNextDate, intervalMeasures);
        if (newMeasure != null) {
          if (newMeasure.fatRatio != null) {
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
    setState(() {
      this.measures = measures;
      this.showFatLine = showFatLine;
    });
  }

  _onSelectionChanged(charts.SelectionModel model) {
    List<charts.SeriesDatum<DateTime>> selectedDatum = model.selectedDatum;

    DateTime date;
    var weight;

    // We get the model that updated with a list of [SeriesDatum] which is
    // simply a pair of series & datum.
    //
    // Walk the selection updating the measures map, storing off the sales and
    // series name for each selection point.
    if (selectedDatum.isNotEmpty) {
      date = selectedDatum.first.datum.date;
      weight = selectedDatum.first.datum.weight;
      selectedDatum.forEach((charts.SeriesDatum<DateTime> datumPair) {
//        print('XXX: ${datumPair.series}');
//        measures[datumPair.series.displayName] = datumPair.datum.sales;
      });
    }

    // Request a build.
    setState(() {
      _selectedDate = date;
      _selectedWeight = weight;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (measures.length == 0 || measures == null) {
      return Container();
    }
    print('$this: Laying out chart with ${measures.length} measures');
    final hasSelected = _selectedDate != null && _selectedWeight != null;
    return Stack(
      children: [
        Positioned(
            top: 10,
            right: 0,
            child: hasSelected
                ? Text(
                    '${yMdFormat.format(_selectedDate)}: ${_selectedWeight.toStringAsFixed(1)}')
                : Container()),
        charts.TimeSeriesChart(
          [
            charts.Series<Measure, DateTime>(
              id: 'Weight',
              colorFn: (_, __) => charts.ColorUtil.fromDartColor(PRIMARY_COLOR),
              domainFn: (Measure measure, _) => measure.date,
              measureFn: (Measure measure, _) => measure.weight,
              data: measures,
            ),
//            charts.Series<Measure, DateTime>(
//              id: 'FatRatio',
//              colorFn: (_, __) => charts.ColorUtil.fromDartColor(ACCENT_COLOR),
//              domainFn: (Measure measure, _) => measure.date,
//              measureFn: (Measure measure, _) => measure.fatRatio,
//              data: measures,
//            )..setAttribute(charts.rendererIdKey, 'FatRatio'),
          ],
          defaultInteractions: true,
          defaultRenderer:
              charts.LineRendererConfig(includePoints: true, includeLine: true),
          customSeriesRenderers: [
//            charts.LineRendererConfig(
//                includePoints: true,
//                includeLine: true,
//                // ID used to link series to this renderer.
//                customRendererId: 'FatRatio'),
//            charts.PointRendererConfig(
//                symbolRenderer: TooltipRenderer2(),
//                // ID used to link series to this renderer.
//                customRendererId: 'FatRatio'),
          ],
          // Custom renderer configuration for the point series.
          // Optionally pass in a [DateTimeFactory] used by the chart. The factory
          // should create the same type of [DateTime] as the data provided. If none
          // specified, the default creates local date time.
          dateTimeFactory: const charts.UTCDateTimeFactory(),
          animate: false,
          behaviors: [
            charts.ChartTitle(widget.title,
                behaviorPosition: charts.BehaviorPosition.top,
                titleOutsideJustification: charts.OutsideJustification.start,
                // Set a larger inner padding than the default (10) to avoid
                // rendering the text too close to the top measure axis tick label.
                // The top tick label may extend upwards into the top margin region
                // if it is located at the top of the draw area.
                innerPadding: 18),
//            charts.LinePointHighlighter(),
//            charts.PanAndZoomBehavior(),
          ],
          primaryMeasureAxis: charts.NumericAxisSpec(
            tickProviderSpec:
                charts.BasicNumericTickProviderSpec(dataIsInWholeNumbers: true),
            viewport: charts.NumericExtents.fromValues(
                measures.map((Measure m) => m.weight)),
          ),
          domainAxis: charts.DateTimeAxisSpec(
            tickProviderSpec:
                charts.AutoDateTimeTickProviderSpec(includeTime: false),
            tickFormatterSpec: charts.AutoDateTimeTickFormatterSpec(),
          ),
          selectionModels: [
            charts.SelectionModelConfig(
              changedListener: _onSelectionChanged,
            ),
          ],
        )
      ],
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
          ..startOf(Units.DAY);
        return j.utc();
      case Interval.WEEK:
        Jiffy j = Jiffy(preferredNextDate)
          ..subtract(weeks: widget.intervalStep * count)
          ..startOf(Units.DAY);
        return j.utc();
      case Interval.MONTH:
        Jiffy j = Jiffy(preferredNextDate)
          ..subtract(months: widget.intervalStep * count)
          ..startOf(Units.DAY);
        return j.utc();
    }
    return null;
  }

  static Measure _processIntervalMeasures(
      DateTime preferredNextDate, List<Measure> intervalMeasures) {
    num weightSum = 0;
    num weightCount = 0;
    num weightMax = -1;
    num weightMin = double.maxFinite;
    num fatSum = 0;
    num fatCount = 0;
    for (Measure intervalMeasure in intervalMeasures) {
      if (intervalMeasure.weight != null) {
        weightSum += intervalMeasure.weight;
        weightCount += 1;
        weightMax = max(intervalMeasure.weight, weightMax);
        weightMin = min(intervalMeasure.weight, weightMin);
      }
      if (intervalMeasure.fatRatio != null) {
        fatSum += intervalMeasure.fatRatio;
        fatCount += 1;
      }
    }
    if (weightCount > 0) {
      var weight = weightSum / weightCount;
      Measure newMeasure = Measure()
        ..weight = weight
        ..date = preferredNextDate
        ..weightError = [weight - weightMin, weightMax - weight];
      if (fatCount > 0) {
        newMeasure.fatRatio = fatSum / fatCount;
      }
      return newMeasure;
    }
    return null;
  }
}

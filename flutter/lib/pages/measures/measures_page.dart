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

import 'package:bikebuds/pages/measures/measures_chart.dart' as measures_chart;
import 'package:bikebuds/pages/measures/measures_state.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class MeasuresPage extends StatefulWidget {
  @override
  _MeasuresPageState createState() => _MeasuresPageState();
}

class _MeasuresPageState extends State<MeasuresPage> {
  bool _fetched = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    print('$this: didChangeDependencies');
    if (!_fetched) {
      _fetched = true;
      print('$this: didChangeDependencies: refresh');
      Provider.of<MeasuresState>(context).refresh().catchError(((err) {
        print('$this: didChangeDependencies: refresh failed: $err');
        _fetched = false;
      }));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: Card(
            child: measures_chart.MeasuresChart(),
          ),
        ),
        Expanded(
          child: Card(
            child: measures_chart.MeasuresChart(
                title: "Daily",
                intervalCount: 90,
                intervalUnit: measures_chart.Interval.DAY),
          ),
        ),
      ],
    );
  }
}

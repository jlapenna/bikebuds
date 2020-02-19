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

import 'package:bikebuds/bikebuds_api_state.dart';
import 'package:bikebuds/pages/measures/measures_chart.dart' as measures_chart;
import 'package:bikebuds/pages/measures/measures_state.dart';
import 'package:bikebuds/user_state.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class MeasuresPage extends StatefulWidget {
  @override
  _MeasuresPageState createState() => _MeasuresPageState();
}

class _MeasuresPageState extends State<MeasuresPage> {
  MeasuresState _measuresState = MeasuresState(filter: "weight");

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProxyProvider2<BikebudsApiState, UserState,
                MeasuresState>(
            create: (_) => _measuresState,
            update: (_, bikebudsApiState, userState, measuresState) =>
                measuresState
                  ..userState = userState
                  ..bikebudsApiState = bikebudsApiState)
      ],
      child: MeasuresWrapper(
        child: Column(
          children: [
            Expanded(
              child: Card(
                child: measures_chart.MeasuresChart(),
              ),
            ),
            Expanded(
              child: Card(
                child: measures_chart.MeasuresChart(
                    title: "Weekly",
                    intervalUnit: measures_chart.Interval.WEEK),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class MeasuresWrapper extends StatefulWidget {
  final Widget child;

  MeasuresWrapper({@required this.child});

  @override
  _MeasuresWrapperState createState() => _MeasuresWrapperState();
}

class _MeasuresWrapperState extends State<MeasuresWrapper> {
  bool _fetched = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    print('$this: didChangeDependencies');
    UserState userState = Provider.of<UserState>(context);
    if (userState.preferences != null && !_fetched) {
      _fetched = true;
      print('$this: didChangeDependencies: refresh');
      Provider.of<MeasuresState>(context).refresh();
    }
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}

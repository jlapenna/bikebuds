import 'package:bikebuds/bikebuds_api_state.dart';
import 'package:bikebuds/user_state.dart';
import 'package:bikebuds_api/api.dart' hide UserState;
import 'package:flutter/foundation.dart';

class MeasuresState with ChangeNotifier {
  String _filter;
  UserState _userState;
  BikebudsApiState _bikebudsApiState;

  var count = 0;
  Series series;
  var unit = 'METRIC';

  MeasuresState({@required filter}) : _filter = filter;

  set bikebudsApiState(BikebudsApiState value) {
    print('MeasuresState: Updated: $value');
    _bikebudsApiState = value;
    notifyListeners();
  }

  set userState(UserState value) {
    _userState = value;
    notifyListeners();
  }

  Future refresh() async {
    if (_bikebudsApiState == null || _userState.preferences == null) {
      print('MeasuresState: Not refreshing');
      return Future.error(Exception('Failed to refresh, not ready.'));
    }
    if (count++ > 4) {
      print('MeasuresState: Not refreshing, too many attempts.');
      return Future.error(Exception('Failed to refresh, too many attempts.'));
    }
    print('MeasuresState: Refreshing');
    return _bikebudsApiState.getSeries(filter: _filter).then((result) {
      print('MeasuresState: Refreshed: ${result.key}');
      _convert(result?.properties);
      this.series = result?.properties;
      notifyListeners();
      return result?.properties;
    }).catchError((err) {
      print('MeasuresState: Failed to refresh: $err');
      notifyListeners();
      return null;
    });
  }

  _convert(Series properties) {
    if (unit != _userState.preferences.units) {
      var conversion =
          _userState.preferences.units == 'METRIC' ? 0.453592 : 2.20462;
      for (Measure m in properties.measures) {
        m.weight *= conversion;
      }
      unit = _userState.preferences.units;
    }
  }
}

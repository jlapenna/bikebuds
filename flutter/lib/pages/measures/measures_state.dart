import 'package:bikebuds/bikebuds_api_state.dart';
import 'package:bikebuds_api/api.dart';
import 'package:flutter/foundation.dart';

class MeasuresState with ChangeNotifier {
  String _filter;
  BikebudsApiState _bikebudsApiState;

  var count = 0;
  Series series;

  MeasuresState({@required filter}) : _filter = filter;

  bool get isReady => _bikebudsApiState?.isReady;

  set bikebudsApiState(BikebudsApiState value) {
    print('MeasuresState: Updated: $value');
    _bikebudsApiState = value;
  }

  Future refresh() async {
    if (_bikebudsApiState == null) {
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
      this.series = result?.properties;
      notifyListeners();
      return result?.properties;
    }).catchError((err) {
      print('MeasuresState: Failed to refresh: $err');
      notifyListeners();
      return null;
    });
  }
}

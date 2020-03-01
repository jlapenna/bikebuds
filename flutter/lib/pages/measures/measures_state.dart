// copyright 2020 google inc. all rights reserved.
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
import 'package:bikebuds/storage/entity_storage.dart';
import 'package:bikebuds/storage/storage.dart';
import 'package:bikebuds/user_state.dart';
import 'package:bikebuds_api/api.dart' hide UserState;
import 'package:flutter/foundation.dart';

class MeasuresState with ChangeNotifier {
  String _filter;

  BikebudsApiState _bikebudsApiState;
  Storage _storage;
  UserState _userState;

  String _unit = 'METRIC';
  SeriesEntity series;

  MeasuresState({@required filter}) : _filter = filter;

  set bikebudsApiState(BikebudsApiState value) {
    print('MeasuresState: Updated: $value');
    _bikebudsApiState = value;
    maybeNotifyListeners();
  }

  set storage(Storage value) {
    _storage = value;
    maybeNotifyListeners();
  }

  set userState(UserState value) {
    _userState = value;
    maybeNotifyListeners();
  }

  maybeNotifyListeners() {
    if (_bikebudsApiState != null &&
        _userState.units != null &&
        _storage != null) {
      notifyListeners();
    }
  }

  Future<SeriesEntity> refresh({bool force: false}) async {
    if (_bikebudsApiState == null ||
        _userState.units == null ||
        _storage == null) {
      print('MeasuresState: Not refreshing');
      return Future.error(Exception('Failed to refresh, not ready.'));
    }
    return await _getOrFetchSeries(force);
  }

  Future<SeriesEntity> _getOrFetchSeries(bool force) async {
    print('MeasuresState: _getOrFetchSeries');
    var series = force ? null : await _storage.seriesStore.get(defaultKey);
    if (series == null) {
      series = await _fetchStoreSeries();
    }
    this.series = _convert(series);
    maybeNotifyListeners();
    return series;
  }

  Future<SeriesEntity> _fetchStoreSeries() async {
    print('MeasuresState: _fetchStoreSeries');
    return await _bikebudsApiState
        .getSeries(filter: _filter)
        .then((SeriesEntity seriesEntity) async {
      print('MeasuresState: Fetched: ${seriesEntity.key}');
      _prepareForStorage(seriesEntity);
      await this._storage.seriesStore.put(seriesEntity);
      notifyListeners();
      return seriesEntity;
    }).catchError((err) {
      print('MeasuresState: Failed to Fetch: $err');
      notifyListeners();
      return null;
    });
  }

  _prepareForStorage(SeriesEntity series) {
    // Overwrite the entity key.
    series.key = EntityKey()..path = defaultKey.path;
  }

  _convert(SeriesEntity series) {
    // Rewrite our data into the user's preferred units.
    var properties = series.properties;
    if (_unit != _userState.units) {
      var conversion = _userState.units == 'METRIC' ? 0.453592 : 2.20462;
      for (Measure m in properties.measures) {
        m.weight *= conversion;
      }
      _unit = _userState.units;
    }
  }
}

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

  MeasuresState({@required filter}) : _filter = filter;

  @override
  toString() {
    return 'MeasuresState(filter=$_filter, isReady=$isReady)';
  }

  set bikebudsApiState(BikebudsApiState value) {
    _bikebudsApiState = value;
    _maybeNotifyListeners();
  }

  set storage(Storage value) {
    _storage = value;
    _maybeNotifyListeners();
  }

  set userState(UserState value) {
    _userState = value;
    _maybeNotifyListeners();
  }

  get isReady =>
      (_bikebudsApiState != null && _userState != null && _storage != null);

  _maybeNotifyListeners() {
    if (isReady) {
      notifyListeners();
    }
  }

  Future<SeriesEntity> get() async {
    if (!isReady) {
      throw Exception('Failed to load, not ready.');
    }
    return await _get();
  }

  Future<SeriesEntity> _get() async {
    print('$this: _get');
    var series = await _storage.seriesStore.get(defaultKey);
    if (series == null) {
      return null;
    }
    return _convert(series);
  }

  Future<SeriesEntity> refresh() async {
    if (!isReady) {
      throw Exception('Failed to refresh, not ready.');
    }
    return await _refresh();
  }

  Future<SeriesEntity> _refresh() async {
    print('$this: _refresh');
    var series = await _fetchStoreSeries();
    if (series == null) {
      return null;
    }
    return _convert(series);
  }

  Future<SeriesEntity> _fetchStoreSeries() async {
    print('$this: _fetchStoreSeries');
    return await _bikebudsApiState
        .getSeries(filter: _filter)
        .then((SeriesEntity seriesEntity) async {
      print(
          '$this: Fetched: ${seriesEntity.key} length: ${seriesEntity.properties?.measures?.length}');
      // Overwrite the entity key.
      seriesEntity.key = EntityKey()..path = defaultKey.path;
      await this._storage.seriesStore.put(seriesEntity);
      _maybeNotifyListeners();
      return seriesEntity;
    }).catchError((err) {
      print('$this: Failed to Fetch: $err');
      _maybeNotifyListeners();
      return null;
    });
  }

  SeriesEntity _convert(SeriesEntity series) {
    // Rewrite our data into the user's preferred units.
    var conversion = _userState.units == 'METRIC' ? 0.453592 : 2.20462;
    for (Measure m in series.properties.measures) {
      m.weight *= conversion;
    }
    return series;
  }
}

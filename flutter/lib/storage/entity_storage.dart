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

import 'dart:convert';

import 'package:bikebuds_api/api.dart';
import 'package:flutter/cupertino.dart';
import 'package:sembast/sembast.dart';

typedef V FromJsonFn<V>(Map<String, dynamic> json);

final EntityKey defaultKey = EntityKey()..path = '__DEFAULT';

class EntityStorage<E extends dynamic> extends ChangeNotifier {
  final Database _db;
  final StoreRef<String, Map<String, dynamic>> _store;
  final FromJsonFn _fromJsonFn;

  EntityStorage(this._db, this._store, this._fromJsonFn);

  @override
  String toString() {
    return 'EntityStorage[${_store.name}]';
  }

  Future<E> get(EntityKey key) async {
    var result = await _store.record(key.path).get(_db);
    print('$this: get: $key ' +
        'putAt ${result == null ? null : result['putAt']}');
    return _convertStoredMap(result);
  }

  Future<E> put(E value) async {
    Map<String, dynamic> valueMap = {
      'key': json.encode(value.key),
      'properties': json.encode(value.properties),
      'putAt': DateTime.now().toUtc().toIso8601String(),
    };
    var resultMap = await _store.record(value.key.path).put(_db, valueMap);
    print('$this: put: ${value.key} putAt ${resultMap['putAt']}');
    notifyListeners();
    return _convertStoredMap(resultMap);
  }

  Future<E> delete(EntityKey key) async {
    var result = await _store.record(key.path).delete(_db);
    notifyListeners();
    return result;
  }

  _convertStoredMap(entityJson) {
    if (entityJson == null) {
      return null;
    }
    return _fromJsonFn({
      'key': json.decode(entityJson['key']),
      'properties': json.decode(entityJson['properties']),
    });
  }
}

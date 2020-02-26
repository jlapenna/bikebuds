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

import 'dart:io';

import 'package:bikebuds/storage/entity_storage.dart';
import 'package:bikebuds_api/api.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sembast/sembast.dart';
import 'package:sembast/sembast_io.dart';

/* Storage that notifies every listener when any data changes. */
class Storage {
  Database _db;
  EntityStorage<ActivityEntity> activityStore;
  EntityStorage<SeriesEntity> seriesStore;
  EntityStorage<UserEntity> userStore;

  Future _loader;

  Future<Storage> load() {
    if (_loader == null) {
      _loader = _load();
    }
    return _loader;
  }

  Future<Storage> _load() async {
    print('Storage: loading');

    Directory appDocDir = await getApplicationDocumentsDirectory();
    String dbPath = appDocDir.path + '/storage.db';

    DatabaseFactory dbFactory = databaseFactoryIo;
    _db = await dbFactory.openDatabase(dbPath);
    activityStore = EntityStorage(_db, stringMapStoreFactory.store('activity'),
        (v) => ActivityEntity.fromJson(v));
    seriesStore = EntityStorage(_db, stringMapStoreFactory.store('series'),
        (v) => SeriesEntity.fromJson(v));
    userStore = EntityStorage(_db, stringMapStoreFactory.store('user'),
        (v) => UserEntity.fromJson(v));
    return this;
  }
}

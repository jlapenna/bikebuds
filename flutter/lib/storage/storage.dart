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
  final Database _db;
  final EntityStorage<ActivityEntity> activityStore;
  final EntityStorage<SeriesEntity> seriesStore;
  final EntityStorage<UserEntity> userStore;

  Storage(Database db)
      : _db = db,
        activityStore = EntityStorage(
            db,
            stringMapStoreFactory.store('activity'),
            (v) => ActivityEntity.fromJson(v)),
        seriesStore = EntityStorage(db, stringMapStoreFactory.store('series'),
            (v) => SeriesEntity.fromJson(v)),
        userStore = EntityStorage(db, stringMapStoreFactory.store('user'),
            (v) => UserEntity.fromJson(v));

  close() async {
    return _db.close();
  }

  static Future<Storage> load() async {
    Directory appDocDir = await getApplicationDocumentsDirectory();
    String dbPath = appDocDir.path + '/storage.db';
    return Storage(await databaseFactoryIo.openDatabase(dbPath));
  }
}

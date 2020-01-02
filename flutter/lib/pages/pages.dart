// Copyright 2019 Google Inc. All Rights Reserved.
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

import 'events/events_page.dart';
import 'home/home_page.dart';
import 'measures/measures_page.dart';
import 'settings/settings_page.dart';

List<Page> createPages(dynamic frontendUrl) {
  return List.unmodifiable([
    Page('Measures', () => MeasuresPage(), null),
    Page('Home', () => HomePage(), "/embed/"),
    Page('Rides', () => EventsPage(), "/embed/events"),
    Page('Settings', () => SettingsPage(), "/embed/settings"),
  ]);
}

class Page {
  final String title;
  final dynamic widgetBuilder;
  final String target;

  const Page(this.title, this.widgetBuilder, this.target);
}

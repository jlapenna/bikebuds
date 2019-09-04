/**
 * Copyright 2019 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React from 'react';
import ReactDOM from 'react-dom';

import MeasuresSummaryCard from './MeasuresSummaryCard';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<MeasuresSummaryCard profile={{}} />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders measures without crashing', () => {
  const div = document.createElement('div');
  var measures = [
    { date: '2014-04-01T15:36:48', heart_pulse: '84', id: '1396366608' },
    {
      date: '2014-04-01T15:36:48',
      fat_free_mass: 61.629,
      fat_mass_weight: 39.218,
      fat_ratio: 38.889,
      id: '1396366608',
      weight: 222.3,
    },
  ];
  ReactDOM.render(
    <MeasuresSummaryCard profile={{}} measures={measures} />,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

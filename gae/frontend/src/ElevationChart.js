/**
 * Copyright 2020 Google Inc. All Rights Reserved.
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

import PropTypes from 'prop-types';
import React, { Component } from 'react';

import { createStyles, withStyles } from '@material-ui/core/styles';

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

class ElevationChart extends Component {
  static styles = createStyles({
    root: {
      minHeight: '300px',
      minWidth: '300px',
    },
  });

  static propTypes = {
    segment: PropTypes.object.isRequired,
  };

  render() {
    return (
      <ResponsiveContainer className={this.props.classes.root}>
        <LineChart
          width={300}
          height={200}
          data={this.props.segment.properties.elevations}
          margin={{ top: 12, right: 12, bottom: 12 }}
        >
          <CartesianGrid stroke="#f5f5f5" />
          <XAxis dataKey="location" height={50} />
          <YAxis />
          <Line
            dataKey="elevation"
            type="monotone"
            connectNulls
            isAnimationActive={false}
            stroke="#03dac6"
            strokeWidth={2}
          ></Line>
        </LineChart>
      </ResponsiveContainer>
    );
  }
}
export default withStyles(ElevationChart.styles)(ElevationChart);

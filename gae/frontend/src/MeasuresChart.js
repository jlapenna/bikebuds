/**
 * Copyright 2018 Google Inc. All Rights Reserved.
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

import { withStyles } from '@material-ui/core/styles';

import moment from 'moment';


import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, Label } from 'recharts';


const styles = {
  root: {
    height:300,
  },
};

class MeasuresChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      measures: undefined,
      weightDomain: ["dataMin - 1", "dataMax + 1"],
      fatDomain: ["dataMin - 1", "dataMax + 1"],
    }
  }

  processMeasures = (newMeasures) => {
    var preferredNextDate = moment.utc().endOf('day');
    var earliestDate = preferredNextDate.clone().subtract(
      this.props.intervalCount, this.props.intervalUnit);
    var measures = [];
    for (var i = 0; i < newMeasures.length; i++) {
      var measure = newMeasures[newMeasures.length - 1 - i];
      var measureDate = moment.utc(measure.date);
      if (measureDate <= earliestDate) {
        break;
      }
      if (measureDate <= preferredNextDate) {
        measures.unshift(measure);
        preferredNextDate.subtract(1, 'seconds').startOf(this.props.intervalUnit);
      }
    };

    this.setState({
      measures: measures,
    });
    console.log('MeasuresChart.processMeasures:', this.state);
  }

  /**
   * @inheritDoc
   */
  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('MeasuresChart.componentDidUpdate', prevProps);
    if (this.state.measures === undefined && this.props.measures) {
      this.processMeasures(this.props.measures);
    }
  }

  render() {
    if (this.state.measures === undefined || this.state.measures.length === 0) {
      console.log('MeasuresChart.render: no measures');
      return null;
    }
    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={this.state.measures}
          margin={{ top: 12, right: 12, left: 12, bottom: 96 }}
        >
          <XAxis
            dataKey="date"
            tickFormatter={
              (tick) => moment.utc(tick).format(this.props.intervalFormat)}
            tick={{ position: "bottom", angle: -45 }}
            textAnchor="end"
            interval="preserveStartEnd"
            padding={{left: 12, right: 12}}
          />
          <YAxis dataKey="weight" yAxisId={0}
            name="Weight"
            tickFormatter={(tick) => tick.toFixed(1)}
            interval={0}
            domain={this.state.weightDomain}
          >
            <Label color="#03dac6" value="Weight" angle={-90} position="left" />
          </YAxis>
          <YAxis dataKey="fat_ratio" yAxisId={1} orientation="right"
            tickFormatter={(tick) => tick.toFixed(1)}
            interval={0}
            domain={this.state.fatDomain}
          >
            <Label value="Fat %" angle={-90} position="right" />
          </YAxis>
          <CartesianGrid stroke="#f5f5f5" />
          <Tooltip
            formatter={(value) => value.toFixed(1)}
            labelFormatter={(value) => moment.utc(value).format('LLL')}
          />
          <Line
            dataKey="weight"
            name="Weight"
            yAxisId={0}
            connectNulls
            isAnimationActive={false}
            stroke="#03dac6"
          />
          <Line
            dataKey="fat_ratio"
            name="Fat %"
            type="monotone"
            yAxisId={1}
            connectNulls
            isAnimationActive={false}
            stroke="#ff4081"
          />
        </LineChart>
      </ResponsiveContainer>
    )
  }
}


MeasuresChart.defaultProps = {
    intervalUnit: 'M',
    intervalCount: 12,
    intervalFormat: "MMM 'YY",
}
MeasuresChart.propTypes = {
  measures: PropTypes.array,
}
export default withStyles(styles)(MeasuresChart);

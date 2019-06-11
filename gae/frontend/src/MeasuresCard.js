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
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import LinearProgress from '@material-ui/core/LinearProgress';
import Typography from '@material-ui/core/Typography';

import moment from 'moment';

import {
  ResponsiveContainer,
  ErrorBar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Label
} from 'recharts';

import { localMoment } from './convert';

class MeasuresCard extends Component {
  static defaultProps = {
    intervalUnit: 'M',
    intervalCount: 12,
    intervalFormat: "MMM 'YY",
    tooltipFormat: 'LLL'
  };

  static propTypes = {
    profile: PropTypes.object.isRequired,
    measures: PropTypes.array
  };

  static styles = {
    root: {
      height: '400px'
    }
  };

  constructor(props) {
    super(props);
    this.state = {
      measures: undefined,
      ticks: [],
      weightDomain: ['dataMin - 1', 'dataMax + 1'],
      fatDomain: ['dataMin - 1', 'dataMax + 1']
    };
  }

  handleMeasures = newMeasures => {
    var preferredNextDate = moment.utc().endOf('day');
    var earliestDate = preferredNextDate
      .clone()
      .subtract(this.props.intervalCount, this.props.intervalUnit);
    var measures = [];
    var ticks = [];
    var intervalMeasures = [];
    for (var i = 0; i < newMeasures.length; i++) {
      var measure = newMeasures[newMeasures.length - 1 - i];
      var measureDate = moment(Number(measure.date));

      intervalMeasures.unshift(measure);

      if (measureDate < preferredNextDate) {
        var weightSum = 0;
        var weightCount = 0;
        var weightMax = -1;
        var weightMin = Number.MAX_SAFE_INTEGER;
        var fatSum = 0;
        var fatCount = 0;
        for (var j = 0; j < intervalMeasures.length; j++) {
          var weight = intervalMeasures[j].weight;
          if (weight !== undefined) {
            weightSum += weight;
            weightCount += 1;
            weightMax = Math.max(weight, weightMax);
            weightMin = Math.min(weight, weightMin);
          }
          if (intervalMeasures[j].fat_ratio !== undefined) {
            fatSum += intervalMeasures[j].fat_ratio;
            fatCount += 1;
          }
        }
        if (weightCount > 0) {
          var weightAvg = weightSum / weightCount;
          var newMeasure = {
            date: preferredNextDate.clone().format('x'),
            weightAvg: weightAvg,
            weightError: [weightAvg - weightMin, weightMax - weightAvg]
          };
          if (fatCount > 0) {
            newMeasure['fat_ratio'] = fatSum / fatCount;
          }
          measures.unshift(newMeasure);
        }
        ticks.unshift(preferredNextDate.clone());
        intervalMeasures = [];
        preferredNextDate
          .subtract(1, 'seconds')
          .startOf(this.props.intervalUnit);
      }
      // Break as necessary.
      if (measureDate <= earliestDate) {
        break;
      }
    }

    this.setState({
      measures: measures,
      ticks: ticks
    });
  };

  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('MeasuresCard.componentDidUpdate', prevProps);
    if (this.state.measures === undefined && this.props.measures) {
      this.handleMeasures(this.props.measures);
    }
  }

  renderChart() {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={this.state.measures}
          margin={{ top: 12, right: 12, left: 12, bottom: 96 }}
        >
          <XAxis
            type="number"
            dataKey="date"
            tickFormatter={tick =>
              localMoment(tick).format(this.props.intervalFormat)
            }
            ticks={this.state.ticks}
            tick={{ position: 'bottom', angle: -45 }}
            domain={['dataMin', 'dataMax']}
            textAnchor="end"
            padding={{ left: 12, right: 12 }}
          />
          <YAxis
            dataKey="weightAvg"
            yAxisId={0}
            name="Weight"
            tickFormatter={tick => tick.toFixed(1)}
            interval={0}
            domain={this.state.weightDomain}
          >
            <Label color="#03dac6" value="Weight" angle={-90} position="left" />
          </YAxis>
          <YAxis
            dataKey="fat_ratio"
            yAxisId={1}
            orientation="right"
            tickFormatter={tick => tick.toFixed(1)}
            interval={0}
            domain={this.state.fatDomain}
          >
            <Label value="Fat %" angle={-90} position="right" />
          </YAxis>
          <CartesianGrid stroke="#f5f5f5" />
          <Tooltip
            formatter={value => value.toFixed(1)}
            labelFormatter={value =>
              moment(Number(value)).format(this.props.tooltipFormat)
            }
          />
          <Line
            dataKey="weightAvg"
            name="Weight"
            type="natural"
            yAxisId={0}
            connectNulls
            isAnimationActive={false}
            stroke="#03dac6"
            strokeWidth={2}
          >
            <ErrorBar
              dataKey="weightError"
              width={4}
              direction="y"
              stroke="#03dac6"
            />
          </Line>
          <Line
            dataKey="fat_ratio"
            name="Fat %"
            type="natural"
            yAxisId={1}
            connectNulls
            isAnimationActive={false}
            stroke="#ff4081"
          />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        <CardContent className={this.props.classes.content}>
          {this.props.title !== undefined && (
            <Typography variant="h5">{this.props.title}</Typography>
          )}
          {this.state.measures === undefined && <LinearProgress />}
          {this.state.measures !== undefined &&
            this.state.measures.length > 0 &&
            this.renderChart()}
        </CardContent>
      </Card>
    );
  }
}
export default withStyles(MeasuresCard.styles)(MeasuresCard);

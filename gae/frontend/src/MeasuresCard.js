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

import { createStyles, withStyles } from '@material-ui/core/styles';
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
} from 'recharts';

import { localMoment } from './convert';

class MeasuresCard extends Component {
  static styles = createStyles({
    root: {
      /* Relative lets the progressIndicator position itself. */
      position: 'relative',
      minHeight: '300px',
    },
    progressIndicator: {
      position: 'absolute',
      left: 0,
      right: 0,
      top: 0,
    },
    content: {
      width: '100%',
      height: '300px',
    },
  });

  static defaultProps = {
    intervalUnit: 'M',
    intervalCount: 12,
    intervalFormat: "MMM 'YY",
    tooltipFormat: 'LLL',
  };

  static propTypes = {
    profile: PropTypes.object.isRequired,
    measures: PropTypes.array,
  };

  constructor(props) {
    super(props);
    this.state = {
      measures: undefined,
      ticks: [],
      showFatLine: false,
    };
  }

  handleMeasures = newMeasures => {
    var preferredNextDate = moment.utc().endOf('day');
    var earliestDate = preferredNextDate
      .clone()
      .subtract(this.props.intervalCount, this.props.intervalUnit);
    var measures = [];
    var ticks = [];
    var showFatLine = false;
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
            weightError: [weightAvg - weightMin, weightMax - weightAvg],
          };
          if (fatCount > 0) {
            newMeasure['fat_ratio'] = fatSum / fatCount;
            showFatLine = true;
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
      ticks: ticks,
      showFatLine: showFatLine,
    });
  };

  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.state.measures === undefined && this.props.measures) {
      this.handleMeasures(this.props.measures);
    }
  }

  renderChart() {
    return (
      <ResponsiveContainer>
        <LineChart
          data={this.state.measures}
          margin={{ top: 12, right: 12, bottom: 12 }}
        >
          <CartesianGrid stroke="#f5f5f5" />
          <Tooltip
            formatter={value => value.toFixed(1)}
            labelFormatter={value =>
              moment(Number(value)).format(this.props.tooltipFormat)
            }
          />
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
            height={50}
          />
          <YAxis
            dataKey="weightAvg"
            yAxisId="weight"
            name="Weight"
            tickFormatter={tick => tick.toFixed(1)}
            interval={0}
            domain={['dataMin - 1', 'dataMax + 1']}
          />
          <Line
            dataKey="weightAvg"
            name="Weight"
            type="natural"
            yAxisId="weight"
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
          {this.state.showFatLine && (
            <YAxis
              dataKey="fat_ratio"
              yAxisId="fat_ratio"
              orientation="right"
              tickFormatter={tick => tick.toFixed(1)}
              interval={0}
              domain={['dataMin - 1', 'dataMax + 1']}
            />
          )}
          {this.state.showFatLine && (
            <Line
              dataKey="fat_ratio"
              name="Fat %"
              type="natural"
              yAxisId="fat_ratio"
              isAnimationActive={false}
              stroke="#ff4081"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.state.measures === undefined && (
          <LinearProgress className={this.props.classes.progressIndicator} />
        )}
        <CardContent className={this.props.classes.content}>
          {this.props.title !== undefined && (
            <Typography variant="h5">{this.props.title}</Typography>
          )}
          {this.state.measures !== undefined &&
            this.state.measures.length > 0 &&
            this.renderChart()}
        </CardContent>
      </Card>
    );
  }
}
export default withStyles(MeasuresCard.styles)(MeasuresCard);

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

import PropTypes from 'prop-types';
import React, { Component } from 'react';

import { createStyles, withStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import LinearProgress from '@material-ui/core/LinearProgress';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import moment from 'moment';

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis } from 'recharts';

import { localMoment } from './convert';

class MeasuresSummaryCard extends Component {
  static styles = createStyles({
    root: {
      /* Relative lets the progressIndicator position itself. */
      position: 'relative',
      minHeight: '320px',
    },
    progressIndicator: {
      position: 'absolute',
      left: 0,
      right: 0,
      top: 0,
    },
    content: {
      minHeight: '320px',
      position: 'relative',
    },
    measuresTable: {
      position: 'absolute',
      top: '0px',
      'z-index': 2,
    },
    measuresChart: {
      position: 'absolute',
      top: '0px',
      'z-index': 1,
      opacity: 0.5,
    },
  });

  static propTypes = {
    profile: PropTypes.object.isRequired,
    measures: PropTypes.array,
  };

  constructor(props) {
    super(props);
    this.state = {
      measures: undefined,
    };
  }

  handleMeasures = newMeasures => {
    if (newMeasures.length === 0) {
      this.setState({
        measures: [],
      });
      return;
    }
    var today = moment(Number(newMeasures[newMeasures.length - 1].date)).endOf(
      'day'
    );
    var weekAgo = today.clone().subtract(1, 'w');
    var monthAgo = today.clone().subtract(1, 'M');
    var sixMonthsAgo = today.clone().subtract(6, 'M');
    var yearAgo = today.clone().subtract(1, 'y');
    var ticks = [yearAgo, sixMonthsAgo, monthAgo, weekAgo, today];
    var ticksIndex = ticks.length - 1;
    var measures = [];
    for (var i = 0; i < newMeasures.length; i++) {
      var measure = newMeasures[newMeasures.length - 1 - i];
      var measureDate = moment(Number(measure.date));
      if (measureDate <= ticks[ticksIndex]) {
        measures.push(measure);
        ticksIndex -= 1;
      }
      if (measureDate <= yearAgo) {
        break;
      }
    }

    this.setState({
      measures: measures,
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
      <React.Fragment>
        <Table size="medium" className={this.props.classes.measuresTable}>
          <TableHead>
            <TableRow>
              <TableCell></TableCell>
              <TableCell>Weight</TableCell>
              <TableCell>Body Fat</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {this.state.measures.map((measure, index) => (
              <TableRow key={index} hover={true}>
                <TableCell>
                  {localMoment(moment(Number(measure.date))).fromNow()}
                </TableCell>
                <TableCell>
                  {measure.weight &&
                    Number.parseFloat(measure.weight).toFixed(2)}
                </TableCell>
                <TableCell>
                  {measure.fat_ratio &&
                    Number.parseFloat(measure.fat_ratio).toFixed(2)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <ResponsiveContainer className={this.props.classes.measuresChart}>
          <LineChart data={this.state.measures}>
            <XAxis
              type="number"
              dataKey="date"
              axisLine={false}
              tick={false}
              tickLine={false}
              domain={['dataMin', 'dataMax']}
            />
            <YAxis
              dataKey="weight"
              yAxisId={0}
              axisLine={false}
              tick={false}
              tickLine={false}
              domain={['dataMin - 1', 'dataMax + 1']}
            />
            <YAxis
              dataKey="fat_ratio"
              yAxisId={1}
              axisLine={false}
              tick={false}
              tickLine={false}
              orientation="right"
              domain={['dataMin - 1', 'dataMax + 1']}
            />
            <Line
              dataKey="weight"
              name="Weight"
              type="monotone"
              yAxisId={0}
              connectNulls
              isAnimationActive={false}
              stroke="#03dac6"
              strokeWidth={2}
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
      </React.Fragment>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.state.measures === undefined && (
          <LinearProgress className={this.props.classes.progressIndicator} />
        )}
        <CardContent className={this.props.classes.content}>
          {this.state.measures !== undefined &&
            this.state.measures.length > 0 &&
            this.renderChart()}
        </CardContent>
      </Card>
    );
  }
}
export default withStyles(MeasuresSummaryCard.styles)(MeasuresSummaryCard);

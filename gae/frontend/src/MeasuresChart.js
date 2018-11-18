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

import React, { Component } from 'react';

import { withStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Grid from '@material-ui/core/Grid';

import moment from 'moment';


import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, Label } from 'recharts';


const styles = {
  root: {
  },
};

class MeasuresChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      measures: undefined,
      syncActionPending: false,
      connectActionPending: false,
      intervalUnit: 'month',
      intervalFormat: 'L',
      earliestInterval: 1,
      earliestUnit: 'years',
    }
  }

  updateMeasuresState = (response) => {
    var syncDate = response.result.sync_successful
      ? moment.utc(response.result.sync_date) : null;

    var preferredNextDate = moment.utc().endOf('day');
    var earliestDate = preferredNextDate.clone().subtract(
      this.state.earliestInterval, this.state.earliestUnit);
    var measures = [];
    response.result.measures.reverse().forEach((measure) => {
      var measureDate = moment.utc(measure.date).startOf('day');
      if ((measureDate <= preferredNextDate) && (measureDate >= earliestDate)) {
        measures.unshift(measure);
        preferredNextDate = preferredNextDate.subtract(
          1, 'seconds').startOf(this.state.intervalUnit);
      }
    });
    this.setState({
      measures: measures,
      created: moment.utc(response.result.created),
      syncDate: syncDate,
      connected: response.result.connected,
    });
    console.log('MeasuresChart.setState: measures: ', measures);
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('MeasuresChart.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.measures === undefined) {
      window.gapi.client.bikebuds.measures().then(this.updateMeasuresState);
    }
  }

  tickFormatterDate = (tickItem) => {
    return moment.utc(tickItem).format(this.state.intervalFormat);
  }

  renderCardContent() {
    if (this.state.measures === undefined) {
      return;
    }
    return (
      <CardContent className={this.props.classes.content}>
        <Grid container
          direction="column"
          justify="center"
          alignItems="center">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart
              data={this.state.measures}
              margin={{ top: 5, right: 20, left: 10, bottom: 60 }}
            >
              <XAxis
                dataKey="date"
                tickFormatter={this.tickFormatterDate}
                tick={{ position: "bottom", angle: -45 }}
                textAnchor="end"
                interval={0}
                domain={this.state.domain} />
              <YAxis dataKey="weight" yAxisId={0}>
                <Label color="#03dac6" value="Weight" angle={-90} position="left" />
              </YAxis>
              <YAxis dataKey="fat_ratio" yAxisId={1} orientation="right">
                <Label value="Fat %" angle={-90} position="right" />
              </YAxis>
              <CartesianGrid stroke="#f5f5f5" />
              <Tooltip />
              <Line type="natural" connectNulls dataKey="weight" stroke="#03dac6" yAxisId={0} />
              <Line type="monotone" connectNulls dataKey="fat_ratio" stroke="#ff4081" yAxisId={1} />
            </LineChart>
          </ResponsiveContainer>
        </Grid>
      </CardContent>
    )
  };

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.renderCardContent()}
      </Card>
    );
  };
}

export default withStyles(styles)(MeasuresChart);

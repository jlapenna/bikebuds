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
import Typography from '@material-ui/core/Typography';

import MeasuresChart from './MeasuresChart';

class MeasuresCard extends Component {
  static defaultProps = {
    intervalUnit: 'M',
    intervalCount: 12,
    intervalFormat: "MMM 'YY"
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

  renderCardContent() {
    return (
      <CardContent className={this.props.classes.content}>
        {this.props.title !== undefined && (
          <Typography variant="h5">{this.props.title}</Typography>
        )}
        <MeasuresChart {...this.props} />
      </CardContent>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.renderCardContent()}
      </Card>
    );
  }
}
export default withStyles(MeasuresCard.styles)(MeasuresCard);

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

import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

class SpinnerScreen extends Component {
  static styles = {
    root: {
      display: 'flex',
      height: '100%',
      width: '100%',
    },
  };

  render() {
    return (
      <Grid
        className={this.props.classes.root}
        container
        spacing={0}
        direction="column"
        alignItems="center"
        justify="center"
      >
        <Grid item>
          <CircularProgress />
        </Grid>
        <Grid item>{this.props.children || <span>&nbsp;</span>}</Grid>
      </Grid>
    );
  }
}
export default withStyles(SpinnerScreen.styles, { withTheme: true })(
  SpinnerScreen
);

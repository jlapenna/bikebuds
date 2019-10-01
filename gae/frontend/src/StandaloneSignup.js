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

import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { withStyles } from '@material-ui/core/styles';

import Signup from './Signup';

class StandaloneSignup extends Component {
  static styles = theme => ({
    root: {
      display: 'flex',
    },
    toolbar: theme.mixins.toolbar,
    appBar: {
      [theme.breakpoints.up('md')]: {
        width: '100%',
        zIndex: theme.zIndex.drawer + 1,
      },
    },
    main: {
      height: '100%',
      width: '100%',
      padding: theme.spacing(2),
    },
  });

  static propTypes = {
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
  };

  render() {
    return (
      <div className={this.props.classes.root} data-testid="standalone-signin">
        <AppBar className={this.props.classes.appBar} position="fixed">
          <Toolbar>
            <Typography
              className={this.props.classes.grow}
              variant="h6"
              color="inherit"
            >
              Bikebuds
            </Typography>
          </Toolbar>
        </AppBar>
        <main className={this.props.classes.main}>
          <div className={this.props.classes.toolbar} />
          <Signup
            firebase={this.props.firebase}
            firebaseUser={this.props.firebaseUser}
          />
        </main>
      </div>
    );
  }
}
export default withStyles(StandaloneSignup.styles, { withTheme: true })(
  StandaloneSignup
);

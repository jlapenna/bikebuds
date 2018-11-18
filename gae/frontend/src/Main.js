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

import AppBar from '@material-ui/core/AppBar';
import Grid from '@material-ui/core/Grid';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { withStyles } from '@material-ui/core/styles';

import GapiWrapper from './GapiWrapper';

import MeasuresChart from './MeasuresChart';
import ProfileCard from './ProfileCard';
import ServiceCard from './ServiceCard';


const styles = {
  root: {
    flexGrow: 1,
  },
  grow: {
    flexGrow: 1,
  },
  menuButton: {
    marginLeft: -12,
    marginRight: 20,
  },
};

class Main extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isSignedIn: undefined,
      gapiReady: false,
    };
    this.onGapiReady = this.onGapiReady.bind(this);
  }

  onGapiReady() {
    this.setState({gapiReady: true});
    console.log('App: gapiReady');
  }

  render() {
    const { classes } = this.props;
    return (
      <div className={classes.root}>
        <AppBar position="static">
          <Toolbar color="inherit" className={classes.grow}>
            <Typography className={classes.grow} variant="h6" color="inherit">Bikebuds</Typography>
          </Toolbar>
        </AppBar>
        <Grid container spacing={24}
          style={{margin: 0, width: '100%'}}>
          <Grid item xs={12}>
            <ProfileCard firebaseUser={this.props.firebaseUser}
              gapiReady={this.state.gapiReady} />
          </Grid>
          <Grid item xs={12}>
            <MeasuresChart
              gapiReady={this.state.gapiReady} />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ServiceCard serviceName="fitbit"
              gapiReady={this.state.gapiReady} />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ServiceCard serviceName="strava"
              gapiReady={this.state.gapiReady} />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ServiceCard serviceName="withings"
              gapiReady={this.state.gapiReady} />
          </Grid>
        </Grid>
        <GapiWrapper onReady={this.onGapiReady} />
      </div>
    );
  };
}

export default withStyles(styles)(Main);

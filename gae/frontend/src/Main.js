import React, { Component } from 'react';

import AppBar from '@material-ui/core/AppBar';
import Grid from '@material-ui/core/Grid';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { withStyles } from '@material-ui/core/styles';

import GapiWrapper from './GapiWrapper';

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

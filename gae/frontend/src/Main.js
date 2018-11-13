import React, { Component } from 'react';
import './App.css';

import CssBaseline from '@material-ui/core/CssBaseline';
import Grid from '@material-ui/core/Grid';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { withStyles, MuiThemeProvider } from '@material-ui/core/styles';
import theme from './theme';

import GapiWrapper from './GapiWrapper';

import ProfileCard from './ProfileCard';
import ServiceCard from './ServiceCard';


const styles = {
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
    return (
      <MuiThemeProvider theme={theme}>
        <React.Fragment>
          <CssBaseline />
          <Grid container spacing={16}
            style={{margin: 0, width: '100%'}}>
            <Grid item>
              <ProfileCard firebaseUser={this.props.firebaseUser}
                gapiReady={this.state.gapiReady} />
            </Grid>
            <Grid item>
              <ServiceCard serviceName="strava"
                gapiReady={this.state.gapiReady} />
            </Grid>
            <Grid item>
              <ServiceCard serviceName="withings"
                gapiReady={this.state.gapiReady} />
            </Grid>
          </Grid>
          <GapiWrapper onReady={this.onGapiReady} />
        </React.Fragment>
      </MuiThemeProvider>
    );
  };
}
export default withStyles(styles)(Main);


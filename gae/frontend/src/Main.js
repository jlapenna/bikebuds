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

import { BrowserRouter as Router, Route, NavLink } from "react-router-dom";

import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import AppBar from '@material-ui/core/AppBar';
import Drawer from '@material-ui/core/Drawer';
import Grid from '@material-ui/core/Grid';
import Hidden from '@material-ui/core/Hidden';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { withStyles } from '@material-ui/core/styles';

import GapiWrapper from './GapiWrapper';

import ActivitiesCard from './ActivitiesCard';
import Home from './Home';
import MeasuresChart from './MeasuresChart';
import PreferencesCard from './PreferencesCard';
import ProfileCard from './ProfileCard';
import ServiceCard from './ServiceCard';
import Settings from './Settings';


const drawerWidth = 240;

const styles = theme => ({
  root: {
    display: 'flex',
  },
  drawerPaper: {
    width: drawerWidth,
  },
  drawer: {
    [theme.breakpoints.up('sm')]: {
      width: drawerWidth,
      flexShrink: 0,
    },
  },
  appBar: {
    marginLeft: drawerWidth,
    [theme.breakpoints.up('sm')]: {
      width: `calc(100% - ${drawerWidth}px)`,
    },
  },
  menuButton: {
    marginRight: 20,
    [theme.breakpoints.up('sm')]: {
      display: 'none',
    },
  },
  toolbar: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    padding: theme.spacing.unit * 3,
  },
  active: {
    backgroundColor: theme.palette.action.selected
  },
});

class Main extends Component {
  constructor(props) {
    super(props);
    this.state = {
      mobileOpen: false,
      isSignedIn: undefined,
      gapiReady: false,
    };
  }

  onDrawerToggle = () => {
    this.setState(state => ({ mobileOpen: !state.mobileOpen }));
  };

  onGapiReady = () => {
    this.setState({gapiReady: true});
  }

  render() {
    const { classes, theme } = this.props;

    const drawerContent = (
      <div>
        <div className={classes.toolbar} />
        <Divider />
        <List>
          <ListItem button key="Home" component={NavLink}
            to="/" exact activeClassName={classes.active}>
            <ListItemText>Home</ListItemText>
          </ListItem>
          <ListItem button key="All" component={NavLink}
            to="/all" exact activeClassName={classes.active}>
            <ListItemText>All</ListItemText>
          </ListItem>
          <ListItem button key="Settings" component={NavLink}
            to="/settings" exact activeClassName={classes.active}>
            <ListItemText>Settings</ListItemText>
          </ListItem>
        </List>
      </div>
    );

    const mainContent = (
      <React.Fragment>
        <Route path="/" exact
          render={() => <Home
            firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady}
          />} />
        <Route path="/settings" exact
          render={() => <Settings
            firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady}
          />} />
        <Route path="/all" exact component={this.renderAll} />
      </React.Fragment>
    );

    return (
      <Router>
      <div className={classes.root}>
        <AppBar className={classes.appBar} position="fixed">
          <Toolbar>
            <IconButton className={classes.menuButton} 
              onClick={this.onDrawerToggle}
              color="inherit"
              aria-label="Menu">
              <MenuIcon />
            </IconButton>
            <Typography className={classes.grow} variant="h6" color="inherit">Bikebuds</Typography>
          </Toolbar>
        </AppBar>
        <nav className={classes.drawer}>
          <Hidden smUp implementation="css">
            <Drawer
              container={this.props.container}
              variant="temporary"
              anchor={theme.direction === 'rtl' ? 'right' : 'left'}
              open={this.state.mobileOpen}
              onClose={this.onDrawerToggle}
              classes={{
                paper: classes.drawerPaper,
              }}
              ModalProps={{
                keepMounted: true, // Better open performance on mobile.
              }}
            >
              {drawerContent}
            </Drawer>
          </Hidden>
          <Hidden xsDown implementation="css">
            <Drawer
              classes={{
                paper: classes.drawerPaper,
              }}
              variant="permanent"
              open
            >
              {drawerContent}
            </Drawer>
          </Hidden>
        </nav>
        <main className={classes.content}>
          <div className={classes.toolbar} />
          {mainContent}
        </main>
        <GapiWrapper onReady={this.onGapiReady} />
      </div>
      </Router>
    );
  };

  renderAll = () => {
    return (
      <Grid container spacing={24}
        style={{margin: 0, width: '100%'}}>
        <Grid item xs={12} sm={12} md={6}>
          <ProfileCard firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady} />
        </Grid>
        <Grid item xs={12} sm={12} md={6}>
          <PreferencesCard firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady} />
        </Grid>
        <Grid item xs={12} sm={12} md={6}>
          <ActivitiesCard
            gapiReady={this.state.gapiReady} />
        </Grid>
        <Grid item xs={12} sm={12} md={6}>
          <MeasuresChart
            gapiReady={this.state.gapiReady} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <ServiceCard serviceName="fitbit"
            gapiReady={this.state.gapiReady} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <ServiceCard serviceName="strava"
            gapiReady={this.state.gapiReady} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <ServiceCard serviceName="withings"
            gapiReady={this.state.gapiReady} />
        </Grid>
      </Grid>
    );
  }
}

export default withStyles(styles, {withTheme: true})(Main);

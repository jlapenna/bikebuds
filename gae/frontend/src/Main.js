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

import { NavLink, Redirect, BrowserRouter as Router, Route, Switch,
    } from "react-router-dom";

import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import AppBar from '@material-ui/core/AppBar';
import Drawer from '@material-ui/core/Drawer';
import Hidden from '@material-ui/core/Hidden';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import LinearProgress from '@material-ui/core/LinearProgress';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { withStyles } from '@material-ui/core/styles';

import Club from './Club';
import FcmWrapper from './FcmWrapper';
import GapiWrapper from './GapiWrapper';
import Home from './Home';
import ProfileWrapper from './ProfileWrapper';
import Settings from './Settings';
import Signup from './Signup';


const drawerWidth = 240;

const styles = (theme) => ({
  root: {
    display: 'flex',
    height: '100%',
  },
  drawerPaper: {
    width: drawerWidth,
  },
  drawer: {
    [theme.breakpoints.up('md')]: {
      width: drawerWidth,
      flexShrink: 0,
    },
  },
  appBar: {
    [theme.breakpoints.up('md')]: {
      width: '100%',
      zIndex: theme.zIndex.drawer + 1,
    },
  },
  menuButton: {
    marginRight: 20,
    [theme.breakpoints.up('md')]: {
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
      isSignedUp: true,
      gapiReady: false,
    };
  }

  onDrawerToggle = () => {
    this.setState(state => ({ mobileOpen: !state.mobileOpen }));
  };

  onGapiReady = () => {
    this.setState({gapiReady: true});
  }

  onMeasuresReady = (measures) => {
    console.log('Main.onMeasuresReady', measures);
    this.setState({measures: measures});
  }

  onPreferencesChanged = (preferences) => {
    console.log('Main.onPreferencesChanged', preferences);
    this.setState((state, props) => {
      state.profile.preferences = preferences;
      return {profile: state.profile};
    });
  }

  onProfileReady = (profile) => {
    console.log('Main.onProfileReady', profile);
    this.setState({
      profile: profile
    });
  }

  onFcmMessage = (payload) => {
    console.log('Main.onFcmMessage', payload);
  }

  renderDrawerContent() {
    if (this.state.profile === undefined) {
      return null;
    }
    if (!this.state.profile.signup_complete) {
      return null;
    }

    return ( 
      <React.Fragment>
        <div className={this.props.classes.toolbar} />
        <List onClick={() => this.setState({mobileOpen: false})}>
          <ListItem button key="Home" component={NavLink}
            to="/" exact activeClassName={this.props.classes.active}>
            <ListItemText>Home</ListItemText>
          </ListItem>
          <ListItem button key="Settings" component={NavLink}
            to="/settings" exact activeClassName={this.props.classes.active}>
            <ListItemText>Settings</ListItemText>
          </ListItem>
        </List>
      </React.Fragment>
    );
  }

  renderMainContent() {
    if (this.state.profile === undefined) {
      return null;
    }
    if (!this.state.profile.signup_complete) {
      return (
        <Switch>
          <Route path="/signup" exact
            render={() => <Signup
              firebaseUser={this.props.firebaseUser}
              gapiReady={this.state.gapiReady}
            />}
          />
          <Route>
            <Redirect to="/signup" />
          </Route>
        </Switch>
      );
    }

    return (
      <Switch>
        <Route path="/club/:club_id"
          render={(thinger) => <Club
            firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady}
            clubId={Number(thinger.match.params.club_id)}
          />}
        />
        <Route path="/" exact
          render={() => <Home
            profile={this.state.profile}
            firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady}
          />}
        />
        <Route path="/settings" exact
          render={() => <Settings
            firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady}
            onPreferencesChanged={this.onPreferencesChanged}
            profile={this.state.profile}
          />}
        />
        <Route path="/signup" exact
          render={() => <Signup
            firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady}
          />}
        />
        <Route>
          <Redirect to="/" />
        </Route>
      </Switch>
    );
  }

  render() {
    return (
      <Router>
      <div className={this.props.classes.root}>
        <GapiWrapper onReady={this.onGapiReady} />
        <ProfileWrapper
          firebaseUser={this.props.firebaseUser}
          gapiReady={this.state.gapiReady}
          onProfileReady={this.onProfileReady}
          profile={this.state.profile}
        />
        <FcmWrapper
          gapiReady={this.state.gapiReady}
          onMessage={this.onFcmMessage}
        />
        <AppBar className={this.props.classes.appBar} position="fixed">
          <Toolbar>
            <IconButton className={this.props.classes.menuButton} 
              onClick={this.onDrawerToggle}
              color="inherit"
              aria-label="Menu">
              <MenuIcon />
            </IconButton>
            <Typography className={this.props.classes.grow} variant="h6" color="inherit">Bikebuds</Typography>
          </Toolbar>
          {this.state.profile === undefined && <LinearProgress />}
        </AppBar>
        <nav className={this.props.classes.drawer}>
          <Hidden mdUp implementation="css">
            <Drawer
              container={this.props.container}
              variant="temporary"
              anchor={this.props.theme.direction === 'rtl' ? 'right' : 'left'}
              open={this.state.mobileOpen}
              onClose={this.onDrawerToggle}
              classes={{
                paper: this.props.classes.drawerPaper,
              }}
              ModalProps={{
                keepMounted: true, // Better open performance on mobile.
              }}
            >
              {this.renderDrawerContent()}
            </Drawer>
          </Hidden>
          <Hidden smDown implementation="css">
            <Drawer
              classes={{
                paper: this.props.classes.drawerPaper,
              }}
              variant="permanent"
              open
            >
              {this.renderDrawerContent()}
            </Drawer>
          </Hidden>
        </nav>
        <main className={this.props.classes.content}>
          <div className={this.props.classes.toolbar} />
          {this.renderMainContent()}
        </main>
      </div>
      </Router>
    );
  };
}

export default withStyles(styles, {withTheme: true})(Main);

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

import {
  NavLink,
  Redirect,
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom';

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
import Events from './Events';
import FcmWrapper from './FcmWrapper';
import GapiWrapper from './GapiWrapper';
import Home from './Home';
import ProfileWrapper from './ProfileWrapper';
import Settings from './Settings';
import Signup from './Signup';

const drawerWidth = 240;

class Main extends Component {
  static styles = theme => ({
    root: {
      display: 'flex',
      height: '100%'
    },
    drawerPaper: {
      width: drawerWidth
    },
    drawer: {
      [theme.breakpoints.up('md')]: {
        width: drawerWidth,
        flexShrink: 0
      },
      height: '100%',
      'text-align': 'center'
    },
    drawerList: {
      height: '100%'
    },
    drawerFooter: {
      bottom: 0
    },
    appBar: {
      [theme.breakpoints.up('md')]: {
        width: '100%',
        zIndex: theme.zIndex.drawer + 1
      }
    },
    menuButton: {
      marginRight: 20,
      [theme.breakpoints.up('md')]: {
        display: 'none'
      }
    },
    toolbar: theme.mixins.toolbar,
    content: {
      flexGrow: 1,
      padding: theme.spacing.unit * 3
    },
    active: {
      backgroundColor: theme.palette.action.selected
    }
  });

  static propTypes = {
    firebaseState: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      mobileOpen: false,
      isSignedUp: true,
      gapiReady: false
    };
  }

  handleDrawerToggle = () => {
    this.setState(state => ({ mobileOpen: !state.mobileOpen }));
  };

  handleGapiReady = () => {
    this.setState({ gapiReady: true });
  };

  handlePreferencesChanged = preferences => {
    console.log('Main.handlePreferencesChanged', preferences);
    this.setState((state, props) => {
      state.profile.preferences = preferences;
      return { profile: state.profile };
    });
  };

  handleProfileReady = profile => {
    console.log('Main.handleProfileReady', profile);
    this.setState({
      profile: profile
    });
  };

  handleFcmMessage = payload => {
    console.log('Main.handleFcmMessage', payload);
  };

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
        <List
          className={this.props.classes.drawerList}
          onClick={() => this.setState({ mobileOpen: false })}
        >
          <ListItem
            button
            key="Home"
            component={NavLink}
            to="/"
            exact
            activeClassName={this.props.classes.active}
          >
            <ListItemText>Home</ListItemText>
          </ListItem>
          <ListItem
            button
            key="Events"
            component={NavLink}
            to="/events"
            exact
            activeClassName={this.props.classes.active}
          >
            <ListItemText>Rides</ListItemText>
          </ListItem>
          <ListItem
            button
            key="Settings"
            component={NavLink}
            to="/settings"
            exact
            activeClassName={this.props.classes.active}
          >
            <ListItemText>Settings</ListItemText>
          </ListItem>
        </List>
        <div className={this.props.classes.drawerFooter}>
          <Typography variant="caption">
            <a href="/privacy">Privacy</a> - <a href="/tos">ToS</a>
          </Typography>
        </div>
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
          <Route
            path="/signup"
            exact
            render={() => (
              <Signup
                firebaseState={this.props.firebaseState}
                firebaseUser={this.props.firebaseUser}
                gapiReady={this.state.gapiReady}
              />
            )}
          />
          <Route>
            <Redirect to="/signup" />
          </Route>
        </Switch>
      );
    }

    return (
      <Switch>
        <Route
          path="/club/:club_id"
          render={thinger => (
            <Club
              firebaseState={this.props.firebaseState}
              firebaseUser={this.props.firebaseUser}
              gapiReady={this.state.gapiReady}
              profile={this.state.profile}
              clubId={Number(thinger.match.params.club_id)}
            />
          )}
        />
        <Route
          path="/"
          exact
          render={() => (
            <Home
              firebaseState={this.props.firebaseState}
              firebaseUser={this.props.firebaseUser}
              gapiReady={this.state.gapiReady}
              profile={this.state.profile}
            />
          )}
        />
        <Route
          path="/events"
          exact
          render={() => (
            <Events
              firebaseState={this.props.firebaseState}
              firebaseUser={this.props.firebaseUser}
              gapiReady={this.state.gapiReady}
              profile={this.state.profile}
            />
          )}
        />
        <Route
          path="/settings"
          exact
          render={() => (
            <Settings
              firebaseState={this.props.firebaseState}
              firebaseUser={this.props.firebaseUser}
              gapiReady={this.state.gapiReady}
              profile={this.state.profile}
              onPreferencesChanged={this.handlePreferencesChanged}
            />
          )}
        />
        <Route
          path="/signup"
          exact
          render={() => (
            <Signup
              firebaseState={this.props.firebaseState}
              firebaseUser={this.props.firebaseUser}
              gapiReady={this.state.gapiReady}
            />
          )}
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
          <GapiWrapper onReady={this.handleGapiReady} />
          <ProfileWrapper
            firebaseState={this.props.firebaseState}
            firebaseUser={this.props.firebaseUser}
            gapiReady={this.state.gapiReady}
            onProfileReady={this.handleProfileReady}
            profile={this.state.profile}
          />
          <FcmWrapper
            firebaseState={this.props.firebaseState}
            gapiReady={this.state.gapiReady}
            onMessage={this.handleFcmMessage}
          />
          <AppBar className={this.props.classes.appBar} position="fixed">
            <Toolbar>
              <IconButton
                className={this.props.classes.menuButton}
                onClick={this.handleDrawerToggle}
                color="inherit"
                aria-label="Menu"
              >
                <MenuIcon />
              </IconButton>
              <Typography
                className={this.props.classes.grow}
                variant="h6"
                color="inherit"
              >
                Bikebuds
              </Typography>
            </Toolbar>
            {this.state.profile === undefined && <LinearProgress />}
          </AppBar>
          <nav className={this.props.classes.drawer}>
            <Hidden mdUp>
              <Drawer
                container={this.props.container}
                variant="temporary"
                anchor={this.props.theme.direction === 'rtl' ? 'right' : 'left'}
                open={this.state.mobileOpen}
                onClose={this.handleDrawerToggle}
                classes={{
                  paper: this.props.classes.drawerPaper
                }}
                ModalProps={{
                  keepMounted: true // Better open performance on mobile.
                }}
              >
                {this.renderDrawerContent()}
              </Drawer>
            </Hidden>
            <Hidden smDown>
              <Drawer
                classes={{
                  paper: this.props.classes.drawerPaper
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
  }
}
export default withStyles(Main.styles, { withTheme: true })(Main);

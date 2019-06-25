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
import Drawer from '@material-ui/core/Drawer';
import Hidden from '@material-ui/core/Hidden';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import LinearProgress from '@material-ui/core/LinearProgress';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { withStyles } from '@material-ui/core/styles';

import DrawerContent from './DrawerContent';
import FcmManager from './FcmManager';
import MainContent from './MainContent';
import ProfileWrapper, { ProfileState } from './ProfileWrapper';
import SwagWrapper from './SwagWrapper';

const drawerWidth = 240;

class Main extends Component {
  static styles = theme => ({
    root: {
      display: 'flex'
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
    toolbar: theme.mixins.toolbar,
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
    main: {
      height: '100%',
      width: '100%',
      padding: theme.spacing(2)
    },
    mainContent: {
      height: '100%',
      width: '100%'
    }
  });

  static propTypes = {
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      mobileOpen: false,
      apiClient: null,
      profile: new ProfileState(this.handleProfileUpdated),
      swagClient: null
    };
  }

  handleDrawerToggle = () => {
    this.setState(state => ({ mobileOpen: !state.mobileOpen }));
  };

  handleSwagReady = client => {
    console.log('Main.handleSwagReady: ', client);
    this.setState({
      apiClient: client.apis
    });
  };

  handleSwagFailed = () => {
    console.log('Main.handleSwagFailed');
    this.setState({
      apiClient: undefined
    });
  };

  handleProfileUpdated = profile => {
    console.log('Main.handleProfileUpdated', profile);
    this.setState({
      profile: profile
    });
  };

  handleFcmMessage = payload => {
    console.log('Main.handleFcmMessage', payload);
  };

  render() {
    return (
      <React.Fragment>
        <div className={this.props.classes.root}>
          <SwagWrapper
            onReady={this.handleSwagReady}
            onFailed={this.handleSwagFailed}
          />
          {this.state.apiClient && (
            <ProfileWrapper
              apiClient={this.state.apiClient}
              profile={this.state.profile}
            />
          )}
          {this.state.apiClient && this.props.firebase !== undefined && (
            <FcmManager
              firebase={this.props.firebase}
              apiClient={this.state.apiClient}
              onMessage={this.handleFcmMessage}
            />
          )}
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
                <div className={this.props.classes.toolbar} />
                <DrawerContent
                  profile={this.state.profile}
                  onClick={() => this.setState({ mobileOpen: false })}
                />
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
                <div className={this.props.classes.toolbar} />
                <DrawerContent
                  profile={this.state.profile}
                  onClick={() => this.setState({ mobileOpen: false })}
                />
              </Drawer>
            </Hidden>
          </nav>
          <main className={this.props.classes.main}>
            <div className={this.props.classes.toolbar} />
            {this.state.apiClient && (
              <MainContent
                className={this.props.classes.mainContent}
                firebase={this.props.firebase}
                firebaseUser={this.props.firebaseUser}
                apiClient={this.state.apiClient}
                profile={this.state.profile}
              />
            )}
          </main>
        </div>
      </React.Fragment>
    );
  }
}
export default withStyles(Main.styles, { withTheme: true })(Main);

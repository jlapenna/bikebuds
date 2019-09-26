/**
 * Copyright 2019 Google Inc. All Rights Reserved.
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
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { withStyles } from '@material-ui/core/styles';

import DrawerContent from './DrawerContent';

const drawerWidth = 240;

class Chrome extends Component {
  static styles = theme => ({
    drawerPaper: {
      width: drawerWidth,
    },
    drawer: {
      [theme.breakpoints.up('md')]: {
        width: drawerWidth,
        flexShrink: 0,
      },
      height: '100%',
      'text-align': 'center',
    },
    main: {
      height: '100%',
      width: '100%',
      padding: theme.spacing(2),
    },
    toolbar: theme.mixins.toolbar,
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
  });
  static propTypes = {
    profile: PropTypes.object,
  };

  constructor(props) {
    super(props);
    this.state = {
      mobileOpen: false,
    };
  }

  handleDrawerToggle = () => {
    this.setState(state => ({ mobileOpen: !state.mobileOpen }));
  };

  render() {
    return (
      <React.Fragment>
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
                paper: this.props.classes.drawerPaper,
              }}
              ModalProps={{
                keepMounted: true, // Better open performance on mobile.
              }}
            >
              <div className={this.props.classes.toolbar} />
              <DrawerContent
                profile={this.props.profile}
                onClick={() => this.setState({ mobileOpen: false })}
              />
            </Drawer>
          </Hidden>
          <Hidden smDown>
            <Drawer
              classes={{
                paper: this.props.classes.drawerPaper,
              }}
              variant="permanent"
              open
            >
              <div className={this.props.classes.toolbar} />
              <DrawerContent
                profile={this.props.profile}
                onClick={() => this.setState({ mobileOpen: false })}
              />
            </Drawer>
          </Hidden>
        </nav>
        <main className={this.props.classes.main}>
          <div className={this.props.classes.toolbar} />
          {this.props.children}
        </main>
      </React.Fragment>
    );
  }
}
export default withStyles(Chrome.styles, { withTheme: true })(Chrome);

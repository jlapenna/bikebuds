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

import React from 'react';
import PropTypes from 'prop-types';

import { NavLink } from 'react-router-dom';

import { createStyles, withStyles } from '@material-ui/core/styles';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Typography from '@material-ui/core/Typography';

class DrawerContent extends React.Component {
  static styles = theme =>
    createStyles({
      list: {
        height: '100%',
      },
      footer: {
        bottom: 0,
      },
      active: {
        backgroundColor: theme.palette.action.selected,
      },
    });

  static propTypes = {
    firebaseUser: PropTypes.object.isRequired,
    profile: PropTypes.object,
  };

  render() {
    if (!this.props.profile) {
      return null;
    }
    if (!this.props.profile.signup_complete) {
      return null;
    }

    const DrawerItemLink = React.forwardRef((props, ref) => (
      <NavLink
        innerRef={ref}
        {...props}
        exact
        activeClassName={this.props.classes.active}
      />
    ));

    return (
      <React.Fragment>
        <List
          className={this.props.classes.list}
          onClick={() => this.props.onClick()}
        >
        {this.props.firebaseUser.roleUser && (
        <React.Fragment>
          <ListItem
            button
            key="Activities"
            component={DrawerItemLink}
            to={{ pathname: '/activities', search: window.location.search }}
          >
            <ListItemText>Activities</ListItemText>
          </ListItem>
          <ListItem
            button
            key="Health"
            component={DrawerItemLink}
            to={{ pathname: '/health', search: window.location.search }}
          >
            <ListItemText>Health</ListItemText>
          </ListItem>
          <ListItem
            button
            key="Settings"
            component={DrawerItemLink}
            to={{ pathname: '/settings', search: window.location.search }}
          >
            <ListItemText>Settings</ListItemText>
          </ListItem>
          </React.Fragment>
          )}
          {this.props.firebaseUser.roleAdmin && (
            <ListItem
              button
              key="Admin"
              component={DrawerItemLink}
              to={{ pathname: '/admin', search: window.location.search }}
            >
              <ListItemText>Admin</ListItemText>
            </ListItem>
          )}
        </List>
        <div className={this.props.classes.footer}>
          <Typography variant="caption">
            <a href="/privacy">Privacy</a> - <a href="/tos">ToS</a>
          </Typography>
        </div>
      </React.Fragment>
    );
  }
}
export default withStyles(DrawerContent.styles)(DrawerContent);

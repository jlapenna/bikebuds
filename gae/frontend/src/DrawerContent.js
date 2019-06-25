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

import { withStyles } from '@material-ui/core/styles';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Typography from '@material-ui/core/Typography';

class DrawerContent extends React.Component {
  static styles = theme => ({
    list: {
      height: '100%'
    },
    footer: {
      bottom: 0
    },
    active: {
      backgroundColor: theme.palette.action.selected
    },
  });

  static propTypes = {
    profile: PropTypes.object
  };

  render() {
    console.log('DrawerContent.render: ', this.props.profile);
    if (!this.props.profile) {
      return null;
    }
    if (!this.props.profile.signup_complete) {
      return null;
    }

    const DrawerItemLink = React.forwardRef((props, ref) => <NavLink innerRef={ref} {...props}
            exact
            activeClassName={this.props.classes.active}
      />);

    return (
      <React.Fragment>
        <List
          className={this.props.classes.list}
          onClick={() => this.props.onClick()}
        >
          <ListItem
            button
            key="Home"
            component={DrawerItemLink}
            to={{ pathname: '/', search: window.location.search }}
          >
            <ListItemText>Home</ListItemText>
          </ListItem>
          <ListItem
            button
            key="Events"
            component={DrawerItemLink}
            to={{ pathname: '/events', search: window.location.search }}
          >
            <ListItemText>Rides</ListItemText>
          </ListItem>
          <ListItem
            button
            key="Settings"
            component={DrawerItemLink}
            to={{ pathname: '/settings', search: window.location.search }}
          >
            <ListItemText>Settings</ListItemText>
          </ListItem>
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

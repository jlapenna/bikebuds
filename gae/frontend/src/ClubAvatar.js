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

import { Link } from 'react-router-dom';

import { createStyles, withStyles } from '@material-ui/core/styles';
import Avatar from '@material-ui/core/Avatar';
import IconButton from '@material-ui/core/IconButton';

class ClubAvatar extends Component {
  static styles = createStyles({
    avatar: {
      'max-height': 32,
      'max-width': 32,
      width: 'auto',
      height: 'auto',
    },
  });

  static propTypes = {
    club: PropTypes.object.isRequired,
  };

  render() {
    return (
      <IconButton
        component={Link}
        to={{
          pathname: `club/${this.props.club.id}`,
          search: window.location.search,
        }}
        alt={this.props.club.name}
      >
        <Avatar
          className={this.props.classes.avatar}
          alt={this.props.club.name}
          src={this.props.club.profile_medium}
        />
      </IconButton>
    );
  }
}
export default withStyles(ClubAvatar.styles)(ClubAvatar);

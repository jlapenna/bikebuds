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

import Fab from '@material-ui/core/Fab';
import AddIcon from '@material-ui/icons/Add';

import { withStyles } from '@material-ui/core/styles';

import EventsListCard from './EventsListCard';

class Events extends Component {
  static styles = theme => ({
    root: {},
    fab: {
      position: 'absolute',
      bottom: theme.spacing(2),
      right: theme.spacing(2),
    },
  });

  static propTypes = {
    firebase: PropTypes.object.isRequired,
    apiClient: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.query = props.firebase.firestore.collection('events');
    this.state = {};
  }

  render() {
    return (
      <div className={this.props.classes.root}>
        <EventsListCard apiClient={this.props.apiClient} query={this.query} />
        <Fab
          color="primary"
          aria-label="Add"
          className={this.props.classes.fab}
        >
          <AddIcon />
        </Fab>
      </div>
    );
  }
}
export default withStyles(Events.styles)(Events);

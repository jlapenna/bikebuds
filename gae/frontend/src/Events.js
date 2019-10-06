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

import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

import ActivitiesListCard from './ActivitiesListCard';
import ActivitiesWrapper from './ActivitiesWrapper';
import EventsListCard from './EventsListCard';

class Events extends Component {
  static styles = {
    root: {
      flexGrow: 1,
    },
  };

  static propTypes = {
    firebase: PropTypes.object.isRequired,
    apiClient: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    if (props.firebase.firestore !== null) {
      this.query = props.firebase.firestore.collection('events');
    } else {
      console.warn('Events: firestore not supported:', props.firebase);
      this.query = null;
    }
    this.state = {};
  }

  render() {
    return this.query !== null ? (
      <Grid className={this.props.classes.root} container spacing={3}>
        <Grid item xs={12}>
          <EventsListCard apiClient={this.props.apiClient} query={this.query} />
        </Grid>
        <Grid item xs={12}>
          <ActivitiesWrapper
            apiClient={this.props.apiClient}
            onResponse={this.handleActivitiesResponse}
            render={wrapperState => (
              <ActivitiesListCard
                apiClient={this.props.apiClient}
                profile={this.props.profile}
                activities={wrapperState.activities}
                showDate={true}
              />
            )}
          />
        </Grid>
      </Grid>
    ) : null;
  }
}
export default withStyles(Events.styles)(Events);

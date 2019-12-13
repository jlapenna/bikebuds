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
import { createStyles, withStyles } from '@material-ui/core/styles';

import BikebudsFetcher from './bikebuds_api';
import RoutesListCard from './RoutesListCard';
import ActivitiesListCard from './ActivitiesListCard';
import EventsListCard from './EventsListCard';

class Events extends Component {
  static styles = createStyles({
    root: {
      flexGrow: 1,
    },
  });

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
    return (
      <Grid className={this.props.classes.root} container spacing={3}>
        <Grid item xs={12}>
          {this.query !== null && (
            <EventsListCard
              apiClient={this.props.apiClient}
              query={this.query}
            />
          )}
        </Grid>
        <Grid item xs={12}>
          <BikebudsFetcher
            fetcher={
              !!this.props.apiClient
                ? this.props.apiClient.bikebuds.get_routes
                : undefined
            }
            params={{}}
            render={wrapperState => (
              <RoutesListCard
                profile={this.props.profile}
                response={wrapperState.response}
                showDate={true}
              />
            )}
          />
        </Grid>
        <Grid item xs={12}>
          <BikebudsFetcher
            fetcher={
              !!this.props.apiClient
                ? this.props.apiClient.bikebuds.get_activities
                : undefined
            }
            params={{}}
            render={wrapperState => (
              <ActivitiesListCard
                profile={this.props.profile}
                response={wrapperState.response}
                showDate={true}
              />
            )}
          />
        </Grid>
      </Grid>
    );
  }
}
export default withStyles(Events.styles)(Events);

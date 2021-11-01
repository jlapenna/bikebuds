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

import ActivitiesListCard from './ActivitiesListCard';
import BikebudsFetcher from './bikebuds_api';

class Activities extends Component {
  static styles = createStyles({
    root: {
      flexGrow: 1,
    },
  });

  static propTypes = {
    bikebudsApi: PropTypes.object.isRequired,
  };

  render() {
    return (
      <Grid className={this.props.classes.root} container spacing={3}>
        <Grid item xs={12}>
          <BikebudsFetcher
            fetcher={this.props.bikebudsApi.get_activities}
            params={{}}
            render={wrapperState => (
              <ActivitiesListCard
                activities={wrapperState.response}
                profile={this.props.profile}
                showDate={true}
              />
            )}
          />
        </Grid>
      </Grid>
    );
  }
}
export default withStyles(Activities.styles)(Activities);

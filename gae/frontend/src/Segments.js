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
import SegmentsListCard from './SegmentsListCard';

class Segments extends Component {
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
            fetcher={this.props.bikebudsApi.get_segments}
            params={{}}
            render={wrapperState => (
              <SegmentsListCard
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
export default withStyles(Segments.styles)(Segments);

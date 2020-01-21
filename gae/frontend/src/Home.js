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

import { createStyles, withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Hidden from '@material-ui/core/Hidden';

import MeasuresCard from './MeasuresCard';
import MeasuresSummaryCard from './MeasuresSummaryCard';
import MeasuresWrapper from './MeasuresWrapper';

class Home extends Component {
  static styles = createStyles({
    root: {
      flexGrow: 1,
    },
  });

  static propTypes = {
    bikebudsApi: PropTypes.object.isRequired,
    profile: PropTypes.object,
  };

  render() {
    return (
      <Grid className={this.props.classes.root} container spacing={3}>
        <MeasuresWrapper
          profile={this.props.profile}
          bikebudsApi={this.props.bikebudsApi}
          render={wrapperState => (
            <React.Fragment>
              <Grid item xs={12}>
                <MeasuresSummaryCard
                  profile={this.props.profile}
                  measures={wrapperState.measures}
                />
              </Grid>
              <Grid item xs={12}>
                <Hidden mdUp>
                  <MeasuresCard
                    profile={this.props.profile}
                    measures={wrapperState.measures}
                    intervalUnit="W"
                    intervalFormat="D MMM 'YY"
                    intervalCount={52}
                    tooltipFormat="D MMM 'YY"
                  />
                </Hidden>
                <Hidden smDown>
                  <MeasuresCard
                    profile={this.props.profile}
                    measures={wrapperState.measures}
                    intervalUnit="W"
                    intervalFormat="D MMM 'YY"
                    intervalCount={208}
                    tooltipFormat="MMM 'YY"
                  />
                </Hidden>
              </Grid>
            </React.Fragment>
          )}
        />
      </Grid>
    );
  }
}
export default withStyles(Home.styles)(Home);

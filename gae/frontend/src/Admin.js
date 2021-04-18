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

import AdminUsers from 'AdminUsers';
import AdminStravaClubs from 'AdminStravaClubs';
import ServiceCard from './ServiceCard';

class Admin extends Component {
  static styles = createStyles({});

  static propTypes = {
    adminApi: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
    };
  }

  componentDidMount() {
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.adminApi && this.state.users === undefined) {
      this.setState({ users: null });
      this.props.adminApi
        .get_users()
        .then(response => this.setState({ users: response }));
    }
  }

  render() {
    return (
      <Grid container spacing={3}>
        <Grid item>
        <ServiceCard
          adminApi={this.props.adminApi}
          firebase={this.props.firebase}
          serviceName={'strava'}
        />
        </Grid>
        <Grid item>
          <ServiceCard
            adminApi={this.props.adminApi}
            firebase={this.props.firebase}
            serviceName={'google'}
          />
        </Grid>
        <Grid item>
        <AdminStravaClubs
          adminApi={this.props.adminApi}
        />
        </Grid>
        <Grid item>
        <AdminUsers
          adminApi={this.props.adminApi}
        />
        </Grid>
      </Grid>
    );
  }
}
export default withStyles(Admin.styles)(Admin);

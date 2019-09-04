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

import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Grid from '@material-ui/core/Grid';
import LinearProgress from '@material-ui/core/LinearProgress';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import Moment from 'react-moment';
import moment from 'moment';
import cloneDeepWith from 'lodash/cloneDeepWith';

import { config } from './config';
import { createSession } from './session_util';

class ServiceCard extends Component {
  static styles = {
    root: {
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    },
    cardContentItem: {
      width: '100%',
    },
  };

  static propTypes = {
    firebase: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      service: undefined,
      actionPending: false,
    };
  }

  handleConnect = () => {
    this.setState({ actionPending: true });
    if (
      this.state.service.properties.credentials !== undefined &&
      this.state.service.properties.credentials
    ) {
      this.props.apiClient.bikebuds
        .disconnect_service({ name: this.props.serviceName })
        .then(response => {
          this.handleService(response);
          this.setState({ actionPending: false });
        });
    } else {
      createSession(this.props.firebase, response => {
        if (response.status === 200) {
          window.location.replace(
            config.frontendUrl +
              '/services/' +
              this.props.serviceName +
              '/init?dest=/settings'
          );
        } else {
          console.log('Unable to create a session.', response);
          this.setState({ actionPending: false });
        }
      });
    }
  };

  handleService = response => {
    response.body.properties.sync_date =
      response.body.properties.sync_successful &&
      !!response.body.properties.sync_date
        ? moment.utc(response.body.properties.sync_date)
        : null;
    response.body.properties.created = moment.utc(
      response.body.properties.created
    );
    response.body.properties.modified = moment.utc(
      response.body.properties.modified
    );
    this.setState({
      service: response.body,
    });
    console.log('ServiceCard.handleService', response.body);
  };

  handleSync = () => {
    this.setState({ actionPending: true });
    this.props.apiClient.bikebuds
      .sync_service({ name: this.props.serviceName })
      .then(response => {
        this.handleService(response);
        this.setState({ actionPending: false });
      });
    return;
  };

  handleSyncSwitchChange = event => {
    if (!this.state.service) {
      return;
    }
    var newState = { service: cloneDeepWith(this.state.service) };
    newState.service.sync_enabled = event.target.checked;

    this.setState(newState);

    this.props.apiClient.bikebuds
      .update_service({
        name: this.props.serviceName,
        payload: { sync_enabled: event.target.checked },
      })
      .then(this.handleService);
  };

  componentDidMount() {
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ServiceCard.componentDidUpdate', prevProps);
    if (this.props.apiClient && this.state.service === undefined) {
      console.log('ServiceCard.componentDidUpdate: apiClient and no state');
      this.props.apiClient.bikebuds
        .get_service({ name: this.props.serviceName })
        .then(this.handleService);
    }
  }

  renderCardContent() {
    return (
      <CardContent className={this.props.classes.content}>
        <Grid container direction="column" justify="center" alignItems="center">
          <Grid item>
            <Typography variant="h5">{this.props.serviceName}</Typography>
            {this.state.service === undefined && <LinearProgress />}
            {this.state.service &&
            this.state.service.properties.sync_date != null ? (
              <i>
                Last sync:{' '}
                <Moment fromNow>
                  {this.state.service.properties.sync_date}
                </Moment>
              </i>
            ) : (
              <i>&#8203;</i>
            )}
          </Grid>
          <Grid className={this.props.classes.cardContentItem} item>
            <FormControlLabel
              control={
                <Switch
                  disabled={
                    this.state.actionPending ||
                    this.state.service === undefined ||
                    !this.state.service.properties.credentials
                  }
                  checked={
                    this.state.service !== undefined &&
                    this.state.service.properties.sync_enabled
                  }
                  onChange={this.handleSyncSwitchChange}
                  value="sync_enabled"
                />
              }
              label="Enabled"
            />
          </Grid>
        </Grid>
      </CardContent>
    );
  }

  renderCardActions() {
    var connectText;
    if (
      this.state.service === undefined ||
      !this.state.service.properties.credentials
    ) {
      connectText = 'Connect';
    } else {
      connectText = 'Disconnect';
    }
    return (
      <CardActions>
        <Button
          color="primary"
          variant="contained"
          disabled={
            this.state.actionPending ||
            this.state.service === undefined ||
            !this.state.service.properties.credentials
          }
          onClick={this.handleSync}
        >
          Sync
          {this.state.actionPending && <CircularProgress size={20} />}
        </Button>
        <Button
          color="secondary"
          disabled={
            this.state.actionPending || this.state.service === undefined
          }
          onClick={this.handleConnect}
        >
          {connectText}
          {this.state.actionPending && <CircularProgress size={20} />}
        </Button>
      </CardActions>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.renderCardContent()}
        {this.renderCardActions()}
      </Card>
    );
  }
}
export default withStyles(ServiceCard.styles)(ServiceCard);

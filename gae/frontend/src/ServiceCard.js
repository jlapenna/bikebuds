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
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Grid from '@material-ui/core/Grid';
import LinearProgress from '@material-ui/core/LinearProgress';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import Moment from 'react-moment';
import moment from 'moment';
import cloneDeepWith from 'lodash/cloneDeepWith';
import makeCancelable from 'makecancelable';

import { config } from './config';
import { createSession } from './session_util';

class ServiceCard extends Component {
  static styles = createStyles({
    root: {
      /* Relative lets the progressIndicator position itself. */
      position: 'relative',
    },
    progressIndicator: {
      position: 'absolute',
      left: 0,
      right: 0,
      top: 0,
    },
    content: {
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    },
    cardContentItem: {
      width: '100%',
    },
    contentGrid: {
      flexGrow: 1,
    },
  });

  static propTypes = {
    bikebudsApi: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    serviceName: PropTypes.string.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      service: undefined,
      actionPending: false,
    };
  }

  componentWillUnmount() {
    if (this._cancelDisconnect) {
      this._cancelDisconnect();
    }
    if (this._cancelSync) {
      this._cancelSync();
    }
  }

  handleConnect = () => {
    this.setState({ actionPending: true });
    if (
      this.state.service.properties.credentials !== undefined &&
      this.state.service.properties.credentials
    ) {
      this._cancelDisconnect = makeCancelable(
        this.props.bikebudsApi.disconnect({
          name: this.props.serviceName,
        }),
        response => {
          this.handleService(response);
          this.setState({ actionPending: false });
        },
        console.error
      );
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
          console.warn('Unable to create a session.', response);
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
  };

  handleSync = () => {
    this.setState({ actionPending: true });
    this._cancelSync = makeCancelable(
      this.props.bikebudsApi.sync_service({
        name: this.props.serviceName,
      }),
      response => {
        this.handleService(response);
        this.setState({ actionPending: false });
      },
      console.error
    );
  };

  handleSyncSwitchChange = event => {
    if (!this.state.service) {
      return;
    }
    var newState = { service: cloneDeepWith(this.state.service) };
    newState.service.sync_enabled = event.target.checked;

    this.setState(newState);

    this.props.bikebudsApi
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
    if (this.props.bikebudsApi && this.state.service === undefined) {
      this.props.bikebudsApi
        .get_service({ name: this.props.serviceName })
        .then(this.handleService);
    }
  }

  renderCardContent() {
    return (
      <CardContent className={this.props.classes.content}>
        <Grid
          className={this.props.classes.contentGrid}
          container
          direction="column"
          justify="center"
          alignItems="center"
        >
          <Grid item>
            <Typography variant="h5">{this.props.serviceName}</Typography>
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
    if (this.state.service === undefined) {
      connectText = '';
    } else if (this.state.service.properties.credentials) {
      connectText = 'Disconnect';
    } else if (this.state.service) {
      connectText = 'Connect';
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
        </Button>
        <Button
          color="secondary"
          disabled={
            this.state.actionPending || this.state.service === undefined
          }
          onClick={this.handleConnect}
        >
          {connectText}
        </Button>
      </CardActions>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        {(this.state.actionPending || this.state.service === undefined) && (
          <LinearProgress className={this.props.classes.progressIndicator} />
        )}
        {this.renderCardContent()}
        {this.renderCardActions()}
      </Card>
    );
  }
}
export default withStyles(ServiceCard.styles)(ServiceCard);

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

import React, { Component } from 'react';

import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Grid from '@material-ui/core/Grid';
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
      'min-height': '200px'
    },
    cardContentItem: {
      width: '100%'
    },
    avatar: {
      width: 60,
      height: 60
    }
  };

  constructor(props) {
    super(props);
    this.state = {
      service: undefined,
      syncActionPending: false,
      connectActionPending: false
    };
  }

  handleConnect = () => {
    this.setState({ connectActionPending: true });
    if (
      this.state.service.credentials !== undefined &&
      this.state.service.credentials
    ) {
      window.gapi.client.bikebuds
        .disconnect_service({ id: this.props.serviceName })
        .then(response => {
          this.handleService(response);
          this.setState({ connectActionPending: false });
        });
    } else {
      createSession(response => {
        if (response.status === 200) {
          window.location.replace(
            config.frontendUrl +
              '/services/' +
              this.props.serviceName +
              '/init?dest=/services/frontend'
          );
        } else {
          console.log('Unable to create a session.', response);
          this.setState({ connectActionPending: false });
        }
      });
    }
  };

  handleService = response => {
    response.result.service.sync_date = response.result.service.sync_successful
      ? moment.utc(response.result.service.sync_date)
      : null;
    response.result.service.created = moment.utc(response.result.created);
    response.result.service.modified = moment.utc(response.result.modified);
    this.setState({
      service: response.result.service
    });
    console.log('ServiceCard.handleService', response.result);
  };

  handleSync = () => {
    this.setState({ syncActionPending: true });
    window.gapi.client.bikebuds
      .sync_service({ id: this.props.serviceName })
      .then(response => {
        this.handleService(response);
        this.setState({ connectActionPending: false });
      });
    return;
  };

  handleSyncSwitchChange = event => {
    if (!this.state.service) {
      return;
    }
    var checked = event.target.checked;
    var newState = { service: cloneDeepWith(this.state.service) };
    newState.service.sync_enabled = checked;

    this.setState(newState);

    window.gapi.client.bikebuds
      .update_service({
        id: this.props.serviceName,
        service: { sync_enabled: event.target.checked }
      })
      .then(this.handleService);
  };

  /**
   * @inheritDoc
   */
  componentDidMount() {
    this.setState({});
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ServiceCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.service === undefined) {
      console.log('ServiceCard.componentDidUpdate: gapiReady and no state');
      window.gapi.client.bikebuds
        .get_service({ id: this.props.serviceName })
        .then(this.handleService);
    }
  }

  renderCardContent() {
    return (
      <CardContent className={this.props.classes.content}>
        <Grid container direction="column" justify="center" alignItems="center">
          <Grid className={this.props.classes.cardContentItem} item>
            <Typography variant="h5">{this.props.serviceName}</Typography>
            {this.state.service && this.state.service.sync_date != null ? (
              <i>
                Last sync:{' '}
                <Moment fromNow>{this.state.service.sync_date}</Moment>
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
                    this.state.syncActionPending ||
                    this.state.service === undefined ||
                    !this.state.service.credentials
                  }
                  checked={
                    this.state.service !== undefined &&
                    this.state.service.sync_enabled
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
    if (this.state.service === undefined || !this.state.service.credentials) {
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
            this.state.syncActionPending ||
            this.state.service === undefined ||
            !this.state.service.credentials
          }
          onClick={this.handleSync}
        >
          Sync
          {this.state.syncActionPending && <CircularProgress size={20} />}
        </Button>
        <Button
          color="secondary"
          disabled={
            this.state.connectActionPending || this.state.service === undefined
          }
          onClick={this.handleConnect}
        >
          {connectText}
          {this.state.connectActionPending && <CircularProgress size={20} />}
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

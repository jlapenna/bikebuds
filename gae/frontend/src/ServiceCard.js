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
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import Moment from 'react-moment';
import moment from 'moment';

import { config } from './Config';
import { createSession } from './session_util';

const styles = {
  root: {
  },
  avatar: {
    width: 60,
    height: 60,
  }
};

class ServiceCard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      service: undefined,
      syncActionPending: false,
      connectActionPending: false,

    }
    this.onConnect = this.onConnect.bind(this);
    this.onSync = this.onSync.bind(this);
    this.updateServiceState = this.updateServiceState.bind(this);
  }

  onConnect() {
    this.setState({connectActionPending: true});
    if (this.state.connected !== undefined && this.state.connected) {
      window.gapi.client.bikebuds.disconnect_service(
        {'id': this.props.serviceName}).then((response) => {
          this.updateServiceState(response);
          this.setState({connectActionPending: false});
        });
      return;
    }
    createSession((response) => {
      if (response.status === 200) {
        window.location.replace(config.frontendUrl + '/services/' +
          this.props.serviceName + '/init?dest=/services/frontend');
      } else {
        console.log('Unable to create a session.', response);
        this.setState({connectActionPending: false});
      }
    });
  }

  onSync() {
    this.setState({syncActionPending: true});
    window.gapi.client.bikebuds.sync_service(
      {'id': this.props.serviceName}).then((response) => {
        this.updateServiceState(response);
        this.setState({connectActionPending: false});
      });
    return;
  }

  updateServiceState(response) {
    var sync_date = response.result.sync_successful
      ? moment.utc(response.result.sync_date) : null;
    this.setState({
      service: response.result,
      created: moment.utc(response.result.created),
      sync_date: sync_date,
      connected: response.result.connected,
    });
    console.log('ServiceCard.setState: service: ', response.result);
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ServiceCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.service === undefined) {
      window.gapi.client.bikebuds.get_service(
        {'id': this.props.serviceName}).then(this.updateServiceState);
    }
  }

  renderCardContent() {
    if (this.state.service === undefined) {
      return;
    }
    return (
        <CardContent className={this.props.classes.content}>
          <Grid container
                direction="column"
                justify="center"
                alignItems="center">
            <Typography variant="h5">{this.props.serviceName}</Typography>
            {this.state.sync_date != null &&
                <i>Last sync: <Moment fromNow>{this.state.sync_date}</Moment></i>
            }
            {!this.state.sync_date &&
                <i>&#8203;</i>
            }
          </Grid>
        </CardContent>
    )
  };

  renderCardActions() {
    if (this.state.service === undefined) {
      return;
    }
    if (this.state.connected) {
      return (
        <CardActions>
          <Button color="primary" variant="contained"
            disabled={this.state.syncActionPending}
            onClick={this.onSync}>Sync
            {this.state.syncActionPending && <CircularProgress size={20} />}
          </Button>
          <Button color="secondary"
            disabled={this.state.connectActionPending}
            onClick={this.onConnect}>Disconnect
            {this.state.connectActionPending && <CircularProgress size={20} />}
          </Button>
        </CardActions>
      )
    } else {
      return (
        <CardActions>
          <Button color="primary" variant="contained"
            disabled={this.state.connectActionPending}
            onClick={this.onConnect}>Connect
            {this.state.connectActionPending && <CircularProgress size={20} />}
          </Button>
        </CardActions>
      )
    }
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.renderCardContent()}
        {this.renderCardActions()}
      </Card>
    );
  };
}

export default withStyles(styles)(ServiceCard);

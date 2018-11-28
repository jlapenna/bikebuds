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
import FormGroup from '@material-ui/core/FormGroup';
import Grid from '@material-ui/core/Grid';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import Moment from 'react-moment';
import moment from 'moment';
import cloneDeepWith from 'lodash/cloneDeepWith';

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
    if (this.state.service.credentials !== undefined && this.state.service.credentials) {
      window.gapi.client.bikebuds.disconnect_service(
        {'id': this.props.serviceName}).then((response) => {
          this.updateServiceState(response);
          this.setState({connectActionPending: false});
        });
    } else {
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

  onHandleChange = (event) => {
    var checked = event.target.checked;
    var newState = {service: cloneDeepWith(this.state.service)};
    newState.service.sync_enabled = checked;

    this.setState(newState);

    window.gapi.client.bikebuds.update_service({
      id: this.props.serviceName,
      service: {sync_enabled: event.target.checked},
    }).then(this.updateServiceState);
  }

  updateServiceState(response) {
    response.result.service.sync_date = response.result.service.sync_successful
      ? moment.utc(response.result.service.sync_date) : null;
    response.result.service.created = moment.utc(response.result.created);
    response.result.service.modified = moment.utc(response.result.modified);
    this.setState({
      service: response.result.service,
    });
    console.log('ServiceCard.setState: service: ', response.result);
  }

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
            {this.state.service.sync_date != null &&
                <i>Last sync: <Moment fromNow>{this.state.service.sync_date}</Moment></i>
            }
            {!this.state.service.sync_date &&
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
    if (this.state.service.credentials) {
      return (
        <CardActions>
          <FormGroup row>
            <Button color="primary" variant="contained"
              disabled={this.state.syncActionPending}
              onClick={this.onSync}>Sync
              {this.state.syncActionPending && <CircularProgress size={20} />}
            </Button>
            <Button color="secondary"
              disabled={this.state.connectActionPending}
              onClick={this.onConnect}>
                Disconnect
                {this.state.connectActionPending && <CircularProgress size={20} />}
            </Button>
            <FormControlLabel
              control={
                <Switch
                  checked={this.state.service.sync_enabled}
                  onChange={this.onHandleChange}
                  value="sync_enabled"
                />
              }
              label="Enabled"
            />
          </FormGroup>
        </CardActions>
      )
    } else {
      return (
        <CardActions>
          <FormGroup row>
            <Button color="primary" variant="contained"
              disabled={this.state.connectActionPending}
              onClick={this.onConnect}>
                Connect
                {this.state.connectActionPending && <CircularProgress size={20} />}
            </Button>
          </FormGroup>
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

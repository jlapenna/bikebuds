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
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import Moment from 'react-moment';
import moment from 'moment';
import cloneDeepWith from 'lodash/cloneDeepWith';
import makeCancelable from 'makecancelable';

class UserPassServiceCard extends Component {
  static styles = createStyles({
    root: {
      /* Relative lets the progressIndicator position itself. */
      position: 'relative',
      minHeight: 200,
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
      username: undefined,
      password: undefined,
    };
  }

  componentDidMount() {
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.bikebudsApi && this.state.service === undefined) {
      this._cancelGetService = makeCancelable(
      this.props.bikebudsApi
        .get_service({ name: this.props.serviceName }),
        this.handleService,
        console.error);
    }
  }

  componentWillUnmount() {
    if (this._cancelGetService) {
      this._cancelGetService();
    }
    if (this._cancelConnectUserPass) {
      this._cancelConnectUserPass();
    }
    if (this._cancelDisconnect) {
      this._cancelDisconnect();
    }
    if (this._cancelSync) {
      this._cancelSync();
    }
    if (this._cancelUpdateService) {
      this._cancelUpdateService();
    }
  }

  handleConnect = (event) => {
    this.setState({ actionPending: true });
    if (
      this.state.service.properties.credentials !== undefined &&
      this.state.service.properties.credentials
    ) {
      this._cancelDisconnect = makeCancelable(
        this.props.bikebudsApi.disconnect({
          name: this.props.serviceName,
        }),
        (response) => {
          this.handleService(response);
          this.setState({ actionPending: false });
        },
        console.error
      );
    } else {
      this._cancelConnectUserPass = makeCancelable(
        this.props.bikebudsApi.connect_userpass({
          name: this.props.serviceName,
          payload: {
            username: this.state.username,
            password: this.state.password,
          },
        }),
        (response) => {
          this.handleService(response);
          this.setState({ actionPending: false });
        },
        console.error
      );
    }
  };

  handleService = (response) => {
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
        payload: {},
      }),
      (response) => {
        this.handleService(response);
        this.setState({ actionPending: false });
      },
      console.error
    );
  };

  handleSyncSwitchChange = (event) => {
    if (!this.state.service) {
      return;
    }
    var newState = { service: cloneDeepWith(this.state.service) };
    newState.service.sync_enabled = event.target.checked;

    this.setState(newState);

    this._cancelUpdateService = makeCancelable(
      this.props.bikebudsApi.update_service({
        name: this.props.serviceName,
        payload: { sync_enabled: event.target.checked },
      }),
      this.handleService,
      console.error);
  };

  renderSyncStatus = () => {
    if (this.state.service === undefined) {
      return (<React.Fragment />);
    }

    if (this.state.service.properties.sync_state.syncing) {
      return (<i>Syncing as of{' '}
          <Moment fromNow>
            {this.state.service.properties.sync_state.updated_at}
          </Moment>
          </i>);
    }
    if (this.state.service.properties.sync_state.successful) {
      return (<i>Sync completed {' '}
          <Moment fromNow>
            {this.state.service.properties.sync_state.updated_at}
          </Moment>
          </i>);
    }
    if (this.state.service.properties.sync_state.error) {
      return (<i>Sync failed at{' '}
          <Moment fromNow>
            {this.state.service.properties.sync_state.updated_at}
          </Moment>
          </i>);
    }

    return (<i></i>);
  }

  renderCardContent() {
    return (
      <CardContent className={this.props.classes.content}>
        <Grid
          className={this.props.classes.contentGrid}
          container
          direction="column"
          justifyContent="center"
          alignItems="center"
        >
          <Grid item>
            <Typography variant="h5">{this.props.serviceName}</Typography>
          </Grid>
          <Grid>
            {this.renderSyncStatus()}
          </Grid>
          <Grid item>
            <React.Fragment>
            {this.state.service === undefined ||
              (!this.state.service.properties.credentials && (
                <form noValidate autoComplete="off">
                  <TextField
                    id="username"
                    label="Username"
                    value={this.state.username}
                    onChange={(event) =>
                      this.setState({ username: event.target.value })
                    }
                  />
                  <br />
                  <TextField
                    id="password"
                    label="Password"
                    type="password"
                    value={this.state.password}
                    onChange={(event) =>
                      this.setState({ password: event.target.value })
                    }
                  />
                </form>
              ))}
            </React.Fragment>
          </Grid>
          <Grid item>
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
export default withStyles(UserPassServiceCard.styles)(UserPassServiceCard);

/**
 * Copyright 2021 Google Inc. All Rights Reserved.
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
import CardHeader from '@material-ui/core/CardHeader';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

import makeCancelable from 'makecancelable';
import JSONPretty from 'react-json-pretty';

import { createSession } from './session_util';

class AdminStravaAuth extends Component {
  static styles = createStyles({});

  static propTypes = {
    adminApi: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      actionPending: false,
      authUrl: null,
      dialogOpen: false,
      bot: undefined,
    };
  }

  componentDidMount() {
    this.setState({});
  }

  componentWillUnmount() {
    if (this._cancelStravaAuth) {
      this._cancelStravaAuth();
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.adminApi && this.state.bot === undefined) {
      this.setState({ bot: null });
      this.props.adminApi
        .get_bot({ name: this.props.serviceName })
        .then(response => this.setState({ bot: response }));
    }
  }

  handleConnect = () => {
    this.setState({ actionPending: true });
    createSession(this.props.firebase, response => {
      if (response.status === 200) {
        this._cancelStravaAuth = makeCancelable(
          this.props.adminApi.get_strava_auth_url(),
          response => {
            this.setState({
              actionPending: false,
              authUrl: response.body.auth_url,
              dialogOpen: true,
            });
          }
        );
      } else {
        console.warn('Unable to create a session.', response);
        this.setState({ actionPending: false });
      }
    });
  };


  render() {
    return (
      <Card>
        <CardHeader title="Strava Bot">
          </CardHeader>
      <CardContent className={this.props.classes.content}>
            {this.state.bot && (
              <JSONPretty
                id="json-pretty"
                data={this.state.bot.body}
              ></JSONPretty>
            )}
                </CardContent>
      <CardActions className={this.props.classes.content}>
            <Button
              color="primary"
              variant="contained"
              disabled={this.state.actionPending}
              onClick={this.handleConnect}
            >
              Connect your strava bot account
            </Button>
              </CardActions>
        <Dialog
          open={this.state.dialogOpen}
          onClose={() => this.setState({ dialogOpen: false })}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">
            {'Authorization Url for Strava'}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              <div>
                Please visit in a browser window signed into the bot account you
                wish to use:
              </div>
              <div>{this.state.authUrl}</div>
            </DialogContentText>
          </DialogContent>
        </Dialog>
      </Card>
    );
  }
}
export default withStyles(AdminStravaAuth.styles)(AdminStravaAuth);

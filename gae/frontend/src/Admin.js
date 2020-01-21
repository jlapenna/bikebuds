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
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

import makeCancelable from 'makecancelable';
import JSONPretty from 'react-json-pretty';

class Admin extends Component {
  static styles = createStyles({
    root: {
      flexGrow: 1,
    },
  });

  static propTypes = {
    adminApi: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
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

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.adminApi && this.state.bot === undefined) {
      this.setState({ bot: null });
      this.props.adminApi
        .get_bot({ name: this.props.serviceName })
        .then(response => this.setState({ bot: response.body }));
    }
  }

  handleConnect = () => {
    this.setState({ actionPending: true });
    this._cancelDisconnect = makeCancelable(
      this.props.adminApi.get_strava_auth_url(),
      response => {
        console.log(response);
        this.setState({
          actionPending: false,
          authUrl: response.body.auth_url,
          dialogOpen: true,
        });
      }
    );
  };

  handleClose = () => {
    this.setState({ dialogOpen: false });
  };

  render() {
    if (!this.props.firebaseUser.admin) {
      return null;
    }
    return (
      <React.Fragment>
        <Button
          color="primary"
          disabled={this.state.actionPending}
          onClick={this.handleConnect}
        >
          Connect your strava bot account
        </Button>
        <Dialog
          open={this.state.dialogOpen}
          onClose={this.handleClose}
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
        <JSONPretty id="json-pretty" data={this.state.bot}></JSONPretty>
      </React.Fragment>
    );
  }
}
export default withStyles(Admin.styles)(Admin);

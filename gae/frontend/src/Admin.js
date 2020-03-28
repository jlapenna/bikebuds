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
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import makeCancelable from 'makecancelable';
import JSONPretty from 'react-json-pretty';

import { createSession } from './session_util';

class Admin extends Component {
  static styles = createStyles({
    root: {
      flexGrow: 1,
    },
  });

  static propTypes = {
    adminApi: PropTypes.object.isRequired,
    bikebudsApi: PropTypes.object.isRequired,
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
      clubs: undefined,
      trackClubId: '',
    };
  }

  componentDidMount() {
    this.setState({});
  }

  componentWillUnmount() {
    if (this._cancelStravaAuth) {
      this._cancelStravaAuth();
    }
    if (this._cancelSyncClub) {
      this._cancelSyncClub();
    }
    if (this._cancelTrackClub) {
      this._cancelTrackClub();
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.adminApi && this.state.bot === undefined) {
      this.setState({ bot: null });
      this.props.adminApi
        .get_bot({ name: this.props.serviceName })
        .then(response => this.setState({ bot: response }));
    }
    if (this.props.adminApi && this.state.clubs === undefined) {
      this.setState({ clubs: null });
      this.props.adminApi
        .get_clubs()
        .then(response => this.setState({ clubs: response }));
    }
    if (this.props.adminApi && this.state.users === undefined) {
      this.setState({ users: null });
      this.props.adminApi
        .get_users()
        .then(response => this.setState({ users: response }));
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

  handleListItemClick = (index, user) => {};

  handleSyncClub = club_id => {
    this.setState({ actionPending: true });
    this._cancelSyncClub = makeCancelable(
      this.props.adminApi.sync_club({ club_id: club_id }),
      response =>
        this.setState((state, props) => {
          for (var i = 0; i < state.clubs.body.length; i++) {
            if (state.clubs.body[i].id === club_id) {
              state.clubs.body[i] = response.body;
            }
          }
          return { clubs: state.clubs, actionPending: false };
        })
    );
  };

  handleUntrackClub = club_id => {
    this._cancelUntrackClub = makeCancelable(
      this.props.adminApi.untrack_club({ club_id: club_id }),
      response => this.setState({ trackClubId: '', clubs: undefined })
    );
  };

  handleTrackClub = event => {
    this._cancelTrackClub = makeCancelable(
      this.props.adminApi.track_club({ club_id: this.state.trackClubId }),
      response => this.setState({ trackClubId: '', clubs: undefined })
    );
  };

  render() {
    if (!this.props.firebaseUser.admin) {
      return null;
    }
    console.log(this.state.users);
    return (
      <React.Fragment>
        <Grid container>
          <Grid item>
            <Typography variant="h5">Bot</Typography>
            <Button
              color="primary"
              variant="contained"
              disabled={this.state.actionPending}
              onClick={this.handleConnect}
            >
              Connect your strava bot account
            </Button>
            {this.state.bot && (
              <JSONPretty
                id="json-pretty"
                data={this.state.bot.body}
              ></JSONPretty>
            )}
            <form noValidate autoComplete="off" onSubmit={this.handleTrackClub}>
              <TextField
                id="track-club-id"
                label="Club ID"
                value={this.state.trackClubId}
                onChange={event =>
                  this.setState({ trackClubId: event.target.value })
                }
              />
              <Button
                color="primary"
                variant="contained"
                disabled={this.state.actionPending}
                onClick={this.handleTrackClub}
              >
                Track Club
              </Button>
            </form>
          </Grid>
          {this.state.clubs &&
            this.state.clubs.body.map((club, index) => (
              <Grid item key={index}>
                <Typography variant="h5">
                  Club: {club.properties.name}
                </Typography>
                <Button
                  color="primary"
                  variant="contained"
                  disabled={this.state.actionPending}
                  onClick={() => this.handleSyncClub(club.properties.id)}
                >
                  Sync club
                </Button>
                <Button
                  color="primary"
                  disabled={this.state.actionPending}
                  onClick={() => this.handleUntrackClub(club.properties.id)}
                >
                  Untrack
                </Button>
                {club && <JSONPretty id="json-pretty" data={club}></JSONPretty>}
              </Grid>
            ))}
        </Grid>
        {this.state.users &&
          this.state.users.body.map((user, index) => {
            return (
              <Grid
                item
                key={index}
                onClick={this.handleListItemClick.bind(this, index, user)}
              >
                <Typography variant="h5">
                  User: {user.user.key.path[0].name}
                </Typography>
                <JSONPretty id="json-pretty" data={user}></JSONPretty>
              </Grid>
            );
          })}
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
      </React.Fragment>
    );
  }
}
export default withStyles(Admin.styles)(Admin);

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
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';

import makeCancelable from 'makecancelable';
import JSONPretty from 'react-json-pretty';

class AdminStravaClubs extends Component {
  static styles = createStyles({});

  static propTypes = {
    adminApi: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      actionPending: false,
      bot: undefined,
      clubs: undefined,
      trackClubId: '',
    };
  }

  componentDidMount() {
    this.setState({});
  }

  componentWillUnmount() {
    if (this._cancelSyncClub) {
      this._cancelSyncClub();
    }
    if (this._cancelTrackClub) {
      this._cancelTrackClub();
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.adminApi && this.state.clubs === undefined) {
      this.setState({ clubs: null });
      this.props.adminApi
        .get_clubs()
        .then(response => this.setState({ clubs: response }));
    }
  }

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
    return (
      <React.Fragment>
      <Card>
        <CardHeader title="Strava Clubs" />
        <CardActions>
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
        </CardActions>
        </Card>
        <Grid container spacing={3}>
          {this.state.clubs &&
            this.state.clubs.body.map((club, index) => (
          <Grid item>
          <Card key={index}>
            <CardHeader title={"Club: " + club.properties.name} />
            <CardActions>
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
            </CardActions>
            <CardContent>
              {club && <JSONPretty id="json-pretty" data={club}></JSONPretty>}
            </CardContent>
          </Card>
          </Grid>
            ))}
          </Grid>
          </React.Fragment>
    );
  }
}
export default withStyles(AdminStravaClubs.styles)(AdminStravaClubs);

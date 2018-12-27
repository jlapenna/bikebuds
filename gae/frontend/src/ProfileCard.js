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

import firebase from 'firebase/app';
import 'firebase/auth';

import { withStyles } from '@material-ui/core/styles';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import { config } from './Config';
import { createSession } from './session_util';
import ClubAvatar from './ClubAvatar';

const styles = {
  root: {
    height:300,
  },
  avatar: {
    width: 128,
    height: 128,
  },
  clubContainer: {
    "min-height": 56,
  },
};

class ProfileCard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      profile: undefined,
      connectActionPending: false,
    }
    this.onSignOut = this.onSignOut.bind(this);
    this.onConnectServices = this.onConnectServices.bind(this);
  }

  onSignOut() {
    firebase.auth().signOut().then(() => {
      window.location.reload();
    });
  };

  onConnectServices() {
    this.setState({connectActionPending: true});
    createSession((response) => {
      if (response.status === 200) {
        window.location.replace(config.frontendUrl + '/services/signup');
      } else {
        console.log('Unable to create a session.', response);
      }
    });
  };

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ProfileCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.profile === undefined) {
      console.log('ProfileCard.componentDidUpdate: user');
      window.gapi.client.bikebuds.get_profile().then((response) => {
        this.setState({
          profile: response.result,
        });
        console.log('ProfileCard.setState: profile: ', response.result);
      });
    }
  }

  renderClubs() {
    if (!this.state.profile || !this.state.profile.athlete) {
      return null;
    }
    return (
      <React.Fragment>
        {this.state.profile.athlete.clubs.map((club, index) => {
          return (
            <Grid item key={index}>
              <ClubAvatar club={club} />
            </Grid>
          );
        })
        }
      </React.Fragment>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        <CardContent className={this.props.classes.content}>
          <Grid container
            direction="column"
            justify="space-evenly"
            alignItems="center">
            <Grid item>
              <Avatar className={this.props.classes.avatar}
                alt={this.props.firebaseUser.displayName}
                src={this.props.firebaseUser.photoURL}>
              </Avatar>
              <Typography variant="h5">{this.props.firebaseUser.displayName}</Typography>
            </Grid>
            <Grid item>
              <Grid className={this.props.classes.clubContainer} container
                direction="row"
                justify="space-evenly"
                alignItems="center"
              >
                {this.renderClubs()}
              </Grid>
            </Grid>
          </Grid>
        </CardContent>
        <CardActions>
          <Button color="primary" variant="contained"
            disabled={this.state.connectActionPending}
            onClick={this.onConnectServices}>Connect Services
            {this.state.connectActionPending && <CircularProgress size={20} />}
          </Button>
          <Button color="secondary"
            onClick={this.onSignOut}>Sign-out</Button>
        </CardActions>
      </Card>
    );
  };
}

export default withStyles(styles)(ProfileCard);

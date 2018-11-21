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

import Moment from 'react-moment';
import moment from 'moment';

import { config } from './Config';
import { createSession } from './session_util';

const styles = {
  root: {
    height:300,
  },
  avatar: {
    width: 128,
    height: 128,
  }
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
          created: moment.utc(response.result.created),
        });
        console.log('ProfileCard.setState: profile: ', response.result);
      });
    }
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        <CardContent className={this.props.classes.content}>
          <Grid container
                direction="column"
                justify="center"
                alignItems="center">
            <Avatar className={this.props.classes.avatar}
                    alt={this.props.firebaseUser.displayName}
                    src={this.props.firebaseUser.photoURL}>
            </Avatar>
            <Typography variant="h5">{this.props.firebaseUser.displayName}</Typography>
            {this.state.profile &&
                <i>Joined <Moment fromNow>{this.state.created}</Moment></i>
            }
            {!this.state.profile &&
                <i>&#8203;</i>
            }
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

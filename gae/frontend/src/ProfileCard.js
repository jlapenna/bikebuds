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

import { Link } from 'react-router-dom';

import { createStyles, withStyles } from '@material-ui/core/styles';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import ClubAvatar from './ClubAvatar';

class ProfileCard extends Component {
  static propTypes = {
    bikebudsApi: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
    match: PropTypes.object.isRequired,
    profile: PropTypes.object,
  };

  static styles = createStyles({
    root: {
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    },
    avatar: {
      width: 128,
      height: 128,
    },
    clubContainer: {
      'min-height': 56,
    },
  });

  constructor(props) {
    super(props);
    this.state = {
      connectActionPending: false,
    };
  }

  handleSignOut = () => {
    this.props.firebase.signOut().then(() => {
      window.location.reload();
    });
  };

  componentDidMount() {
    this.setState({});
  }

  renderClubs() {
    if (!this.props.profile || !this.props.profile.athlete) {
      return null;
    }
    return (
      <React.Fragment>
        {!!this.props.profile.athlete.properties.clubs &&
          this.props.profile.athlete.properties.clubs.map((club, index) => {
            return (
              <Grid item key={index}>
                <ClubAvatar club={club} match={this.props.match} />
              </Grid>
            );
          })}
      </React.Fragment>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        <CardContent className={this.props.classes.content}>
          <Grid
            container
            direction="column"
            justify="space-evenly"
            alignItems="center"
          >
            <Grid item>
              <Avatar
                className={this.props.classes.avatar}
                alt={this.props.firebaseUser.displayName}
                src={this.props.firebaseUser.photoURL}
              />
            </Grid>
            <Grid item>
              <Typography variant="h5">
                {this.props.firebaseUser.displayName}{' '}
                {this.props.firebaseUser.roleAdmin && <span>(Admin)</span>}
              </Typography>
            </Grid>
            <Grid item>
              <Typography variant="h6">
                {!!this.props.profile.athlete.properties.city ? (
                  <span>{this.props.profile.athlete.properties.city}</span>
                ) : (
                  <span>&#8203;</span>
                )}
              </Typography>
            </Grid>
            <Grid item>
              <Grid
                className={this.props.classes.clubContainer}
                container
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
          <Button
            color="primary"
            variant="contained"
            component={Link}
            to={{
              pathname: `${this.props.match.url}/signup`,
              search: window.location.search,
            }}
            disabled={this.state.connectActionPending}
          >
            Connect Services
          </Button>
          <Button color="secondary" onClick={this.handleSignOut}>
            Sign-out
          </Button>
        </CardActions>
      </Card>
    );
  }
}
export default withStyles(ProfileCard.styles)(ProfileCard);

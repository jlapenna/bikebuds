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

import { withStyles } from '@material-ui/core/styles';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';


class Club extends Component {

  static propTypes = {
    clubId: PropTypes.number.isRequired,
  }

  static styles = {
    root: {
      width: "360px",
    },
    media: {
      height: "176px",
      width: "360px",
    },
  }

  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      club: undefined,
    }
  }

  updateClubState = (response) => {
    console.log('ClubWrapper.updateClubState:', response);
    if (response.result.club !== undefined) {
      this.setState({
        club: response.result.club,
      });
    }
  }

  /**
   * @inheritDoc
   */
  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ClubWrapper.componentDidUpdate', prevProps);
    if (this.props.gapiReady
      && !this.state.fetched
      && this.state.club === undefined) {
      this.setState({fetched: true});
      window.gapi.client.bikebuds.get_club(
          {id: this.props.clubId}).then(this.updateClubState);
    }
  }

  render() {
    if (this.state.club === undefined) {
      return null;
    }
    return (
      <Card className={this.props.classes.root}>
        <CardMedia
          className={this.props.classes.media}
          image={this.state.club.cover_photo_small}
          title="Contemplative Reptile"
        >
              <Avatar className={this.props.classes.avatar}
                alt={this.state.club.name}
                src={this.state.club.profile_medium}>
              </Avatar>
        </CardMedia>
        <CardContent className={this.props.classes.content}>
          <Grid container
            direction="column"
            justify="space-evenly"
            alignItems="center">
            <Grid item>
              <Typography variant="h5">{this.state.club.name}</Typography>
            </Grid>
            <Grid item>
              <Grid container className={this.props.classes.clubContainer}
                direction="row"
                justify="space-evenly"
                alignItems="center"
              >
                {this.state.club.members.map((member, index) => {
                  var url = '';
                  return (
                    <Grid item key={index}>
                      <Button alt={member.firstname} href={url}>
                        <Avatar
                          alt={member.firstname}
                          src={member.profile_medium} />
                        <Typography>{member.firstname} {member.lastname}</Typography>
                      </Button>
                    </Grid>
                  );
                })
                }
              </Grid>
            </Grid>
          </Grid>
        </CardContent>
        <CardActionArea>
        </CardActionArea>
      </Card>
    );
  };
}

export default withStyles(Club.styles)(Club);

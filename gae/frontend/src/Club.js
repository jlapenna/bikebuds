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

import ActivitiesListCard from './ActivitiesListCard';

class ClubFetcher extends Component {
  static propTypes = {
    clubId: PropTypes.number.isRequired,
    apiClient: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      club: undefined,
      activities: undefined,
      error: undefined
    };
  }

  handleActivities = response => {
    console.log('Club.handleActivities:', response);
    if (response.status !== 200) {
      this.setState({
        activities: null
      });
      return;
    }
    this.setState({
      activities: response.body
    });
  };

  handleClub = response => {
    console.log('Club.handleClub:', response);
    if (response.status !== 200) {
      this.setState({
        club: null,
        error: response.message
      });
      return;
    }
    this.setState({
      club: response.body
    });
  };

  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('Club.componentDidUpdate', prevProps);
    if (
      this.props.apiClient &&
      !this.state.fetched &&
      this.state.club === undefined
    ) {
      this.setState({ fetched: true });
      this.props.apiClient.bikebuds
        .get_club({ club_id: this.props.clubId })
        .then(this.handleClub, this.handleClub);
      this.props.apiClient.bikebuds
        .get_club_activities({ club_id: this.props.clubId })
        .then(this.handleActivities, this.handleActivities);
    }
  }

  render() {
    return this.props.render(this.state);
  }
}

class _ClubWidget extends Component {
  static styles = {
    root: {
      width: '100%'
    },
    card: {
      height: '400px'
    },
    media: {
      height: '176px',
      width: '360px'
    }
  };

  static propTypes = {
    profile: PropTypes.object.isRequired,
    activities: PropTypes.array,
    club: PropTypes.object,
    error: PropTypes.string
  };

  render() {
    console.log('ClubWidget.render', this.props);
    if (this.props.club === undefined) {
      return null;
    }
    if (this.props.club === null) {
      return <React.Fragment>{this.props.error}</React.Fragment>;
    }

    return (
      <div className={this.props.classes.root}>
        <Grid
          className={this.props.classes.contentGridElement}
          container
          spacing={24}
        >
          <Grid
            className={this.props.classes.contentGridElement}
            item
            xs={12}
            md={3}
          >
            <Card className={this.props.classes.card}>
              {/*This causes an error when there is no profile photo:
                "index.js:1446 Warning: Material-UI: either `image` or `src`
                property must be specified." */}
              <CardMedia
                className={this.props.classes.media}
                image={this.props.club.properties.cover_photo_small}
                title="Club Photo"
              >
                <Avatar
                  className={this.props.classes.avatar}
                  alt={this.props.club.properties.name}
                  src={this.props.club.properties.profile_medium}
                />
              </CardMedia>
              <CardContent className={this.props.classes.content}>
                <Grid
                  container
                  direction="column"
                  justify="space-evenly"
                  alignItems="center"
                >
                  <Grid item>
                    <Typography variant="h5">{this.props.club.properties.name}</Typography>
                  </Grid>
                  <Grid item>
                    <Grid
                      container
                      className={this.props.classes.membersContainer}
                      direction="row"
                      justify="space-evenly"
                      alignItems="center"
                    >
                      {this.props.club.properties.members.map((member, index) => {
                        var url = '';
                        return (
                          <Grid item key={index}>
                            <Button alt={member.firstname} href={url}>
                              <Avatar
                                alt={member.firstname}
                                src={member.profile_medium}
                              />
                              <Typography>
                                {member.firstname} {member.lastname}
                              </Typography>
                            </Button>
                          </Grid>
                        );
                      })}
                    </Grid>
                  </Grid>
                </Grid>
              </CardContent>
              <CardActionArea />
            </Card>
          </Grid>
          <Grid
            className={this.props.classes.contentGridElement}
            item
            xs={12}
            md={9}
          >
            <ActivitiesListCard
              apiClient={this.props.apiClient}
              profile={this.props.profile}
              activities={this.props.activities}
              showAthlete={true}
              showDate={true}
            />
          </Grid>
        </Grid>
      </div>
    );
  }
}
export const ClubWidget = withStyles(_ClubWidget.styles)(_ClubWidget);

export default class Club extends Component {
  static propTypes = {
    clubId: PropTypes.number.isRequired,
    apiClient: PropTypes.object.isRequired,
    profile: PropTypes.object.isRequired
  };

  render() {
    return (
      <ClubFetcher
        {...this.props}
        render={state => {
          return <ClubWidget {...state} {...this.props} />;
        }}
      />
    );
  }
}

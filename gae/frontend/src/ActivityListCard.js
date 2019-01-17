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
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Grid from '@material-ui/core/Grid';
import Hidden from '@material-ui/core/Hidden';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Typography from '@material-ui/core/Typography';

import ActivityDetail from './ActivityDetail';

class ActivityListCard extends Component {
  static styles = {
    root: {
      height: '400px'
    },
    content: {
      height: '400px'
    },
    contentGridElement: {
      height: '100%',
      overflow: 'auto'
    }
  };

  static propTypes = {
    profile: PropTypes.object,
    showAthlete: PropTypes.bool
  };

  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      activities: undefined,
      selectedActivity: undefined,
      selectedIndex: undefined
    };
  }

  handleListItemClick = (index, activity) => {
    this.setState({
      selectedActivity: activity,
      selectedIndex: index
    });
  };

  handleUpdateActivities = response => {
    var activities = response.result.activities || [];

    if (activities.length > 0) {
      var selectedActivity = activities[0];
      var selectedindex = 0;
    }

    this.setState({
      activities: activities,
      selectedActivity: selectedActivity,
      selectedIndex: selectedindex
    });
  };

  renderCardContent() {
    if (this.props.activities === undefined) {
      return;
    }
    return (
      <Grid
        className={this.props.classes.contentGridElement}
        container
        spacing={24}
      >
        <Grid
          className={this.props.classes.contentGridElement}
          item
          xs={12}
          sm={4}
          lg={4}
        >
          <List>
            {this.props.activities.map((activity, index) => {
              var fullName = undefined;
              if (this.props.showAthlete && activity.athlete !== undefined) {
                if (activity.athlete.firstname !== undefined) {
                  fullName = activity.athlete.firstname;
                }
                if (activity.athlete.lastname !== undefined) {
                  fullName = fullName + ' ' + activity.athlete.lastname;
                }
              }
              return (
                <ListItem
                  key={index}
                  onClick={this.handleListItemClick.bind(this, index, activity)}
                  selected={this.state.selectedIndex === index}
                >
                  <ListItemText primary={activity.name} secondary={fullName} />
                </ListItem>
              );
            })}
          </List>
        </Grid>
        <Grid
          className={this.props.classes.contentGridElement}
          item
          xs={false}
          sm={8}
          lg={8}
        >
          <Hidden xsDown>
            <ActivityDetail
              profile={this.props.profile}
              activity={this.state.selectedActivity}
            />
          </Hidden>
        </Grid>
      </Grid>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        <CardContent className={this.props.classes.content}>
          <Typography variant="h5">Activities</Typography>
          {this.renderCardContent()}
        </CardContent>
      </Card>
    );
  }
}
export default withStyles(ActivityListCard.styles)(ActivityListCard);

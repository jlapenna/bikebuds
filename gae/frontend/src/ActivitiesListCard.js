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
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Grid from '@material-ui/core/Grid';
import Hidden from '@material-ui/core/Hidden';
import LinearProgress from '@material-ui/core/LinearProgress';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Typography from '@material-ui/core/Typography';

import moment from 'moment';

import ActivityDetail from './ActivityDetail';

class ActivitiesListCard extends Component {
  static styles = createStyles({
    root: {
      /* Relative lets the progressIndicator position itself. */
      position: 'relative',
    },
    progressIndicator: {
      position: 'absolute',
      left: 0,
      right: 0,
      top: 0,
    },
    content: {
      height: '400px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    },
    contentGridElement: {
      height: '100%',
      overflow: 'auto',
    },
  });

  static propTypes = {
    activities: PropTypes.object,
    profile: PropTypes.object,
    showAthlete: PropTypes.bool,
    showDate: PropTypes.bool,
    showMovingTime: PropTypes.bool,
  };

  constructor(props) {
    super(props);
    if (
      this.props.activities !== undefined &&
      this.props.activities.body.length > 0
    ) {
      this.state = {
        selectedActivity: this.props.activities.body[0],
        selectedIndex: 0,
      };
    } else {
      this.state = {};
    }
  }

  handleListItemClick = (index, activity) => {
    this.setState({
      selectedActivity: activity,
      selectedIndex: index,
    });
  };

  handleUpdateActivities = activities => {
    activities = activities || [];

    if (activities.length > 0) {
      var selectedActivity = activities[0];
      var selectedIndex = 0;
    }

    this.setState({
      selectedActivity: selectedActivity,
      selectedIndex: selectedIndex,
    });
  };

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (
      this.props.activities !== undefined &&
      this.props.activities !== prevProps.activities &&
      this.props.activities.body.length > 0
    ) {
      this.setState({
        selectedActivity: this.props.activities.body[0],
        selectedIndex: 0,
      });
    }
  }

  renderCardContent() {
    if (this.props.activities === undefined) {
      return;
    }
    return (
      <Grid
        className={this.props.classes.contentGridElement}
        container
        spacing={3}
      >
        <Grid
          className={this.props.classes.contentGridElement}
          item
          xs={12}
          sm={4}
          lg={4}
        >
          <List>
            {this.props.activities.body.map((activity, index) => {
              var fullName = undefined;
              if (
                this.props.showAthlete &&
                activity.properties.athlete !== undefined
              ) {
                if (activity.properties.athlete.firstname !== undefined) {
                  fullName = activity.properties.athlete.firstname;
                }
                if (activity.properties.athlete.lastname !== undefined) {
                  fullName =
                    fullName + ' ' + activity.properties.athlete.lastname;
                }
              }
              var startDate = undefined;
              if (this.props.showDate) {
                startDate = moment(activity.properties.start_date_local).format(
                  'LLL'
                );
              }

              var secondary = undefined;
              if (fullName !== undefined && startDate !== undefined) {
                secondary = fullName + ' \u2022 ' + startDate;
              } else if (fullName !== undefined) {
                secondary = fullName;
              } else if (startDate !== undefined) {
                secondary = startDate;
              }
              return (
                <ListItem
                  key={index}
                  onClick={this.handleListItemClick.bind(this, index, activity)}
                  selected={this.state.selectedIndex === index}
                >
                  <ListItemText
                    primary={activity.properties.name}
                    secondary={secondary}
                  />
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
        {this.props.activities === undefined && (
          <LinearProgress className={this.props.classes.progressIndicator} />
        )}
        <CardContent className={this.props.classes.content}>
          <Typography variant="h5">Activities</Typography>
          {this.renderCardContent()}
        </CardContent>
      </Card>
    );
  }
}
export default withStyles(ActivitiesListCard.styles)(ActivitiesListCard);

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

import { withStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Grid from '@material-ui/core/Grid';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Typography from '@material-ui/core/Typography';

import ActivityDetail from './ActivityDetail';

const styles = {
  root: {
    "height": "500px",
  },
  content: {
    "height": "500px",
  },
  contentGridElement: {
    "height": "100%",
    overflow: "auto",
  },
};

class ActivityListCard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      activities: undefined,
      selectedActivity: undefined,
      selectedIndex: undefined,

    }
  }

  updateActivitiesState = (response) => {
    this.setState({
      activities: response.result.activities || [],
    });
    console.log('ActivityListCard.setState: service: ', response.result);
  }

  onListItemClick = (index, activity) => {
    console.log('ActivityListCard.onListItemClick', activity);
    this.setState({
      selectedActivity: activity,
      selectedIndex: index,
    });
    console.log('ActivityListCard.onListItemClick', this.state.activity);
  }

  /**
   * @inheritDoc
   */
  componentDidMount() {
    this.setState({});
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.gapiReady
      && !this.state.fetched
      && this.state.activities === undefined) {
      this.setState({fetched: true});
      window.gapi.client.bikebuds.get_activities().then(this.updateActivitiesState);
    }
  }

  renderCardContent() {
    if (this.state.activities === undefined) {
      return;
    }
    return (
        <CardContent className={this.props.classes.content}>
          <Typography variant="h5">Activities</Typography>
          <Grid className={this.props.classes.contentGridElement} container spacing={24}>
            <Grid className={this.props.classes.contentGridElement} item xs={4}>
              <List>
                {this.state.activities.map((activity, index) => {
                  return (
                    <ListItem
                      key={index}
                      onClick={this.onListItemClick.bind(this, index, activity)}
                      selected={this.state.selectedIndex === index}
                    >
                      <ListItemText>{activity.name}</ListItemText>
                    </ListItem>)
                })
              }
              </List>
            </Grid>
            <Grid className={this.props.classes.contentGridElement} item xs={8}>
              <ActivityDetail activity={this.state.selectedActivity} />
            </Grid>
          </Grid>
        </CardContent>
    )
  };

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.renderCardContent()}
      </Card>
    );
  };
}

export default withStyles(styles)(ActivityListCard);

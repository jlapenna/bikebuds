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
import List from '@material-ui/core/List';
import Typography from '@material-ui/core/Typography';

import ActivityItem from './ActivityItem';

const styles = {
  root: {
    height: 300,
    overflow: "auto"
  },
};

class ActivityListCard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activities: undefined,

    }
  }

  updateActivitiesState = (response) => {
    this.setState({
      activities: response.result.activities || [],
    });
    console.log('ActivityListCard.setState: service: ', response.result);
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
    console.log('ActivityListCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.activities === undefined) {
      console.log('ActivityListCard.componentDidUpdate', 'prevState', prevState, 'newState', this.state)
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
          <List>
            {this.state.activities.map((activity, index) => {
              return <ActivityItem key={index} activity={activity} />
            })
          }
          </List>
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

/**
 * Copyright 2019 Google Inc. All Rights Reserved.
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

import EventDetail from './EventDetail';

class EventsListCard extends Component {
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
    apiClient: PropTypes.object.isRequired,
    query: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      events: [],
      selectedEvent: undefined,
      selectedIndex: undefined
    };
  }

  handleListItemClick = (index, event) => {
    this.setState({
      selectedEvent: event,
      selectedIndex: index
    });
  };

  handleUpdateEvents = snapshot => {
    console.log('EventsListCard.handleUpdateEvents:', snapshot);
    var events = [];
    snapshot.forEach(doc => {
      console.log('Adding event: ', doc);
      events.push(doc.data());
    });

    if (events.length > 0) {
      var selectedEvent = events[0];
      var selectedindex = 0;
    }
    console.log(
      'EventsListCard.handleUpdateEvents: selectedEvent: ',
      selectedEvent
    );
    console.log('EventsListCard.handleUpdateEvents: events: ', events);

    this.setState({
      events: events,
      selectedEvent: selectedEvent,
      selectedIndex: selectedindex
    });
  };

  componentDidMount() {
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('EventsListCard.componentDidUpdate', prevProps);
    if (this.props.apiClient && this.unsubscribe === undefined) {
      console.log(
        'EventsListCard.componentDidUpdate: subscribing to: ',
        this.props.query
      );
      this.unsubscribe = this.props.query.onSnapshot(this.handleUpdateEvents);
    }
  }

  componentWillUnmount() {
    if (this.unsubscribe !== undefined) {
      this.unsubscribe();
      this.unsubscribe = undefined;
    }
  }

  renderCardContent() {
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
            {this.state.events.map((event, index) => {
              console.log('EventsListCard.renderCardContent: ', event);
              return (
                <ListItem
                  key={index}
                  onClick={this.handleListItemClick.bind(this, index, event)}
                  selected={this.state.selectedIndex === index}
                >
                  <ListItemText primary={event.title} />
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
            <EventDetail
              profile={this.props.profile}
              event={this.state.selectedEvent}
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
          <Typography variant="h5">Events</Typography>
          {this.renderCardContent()}
        </CardContent>
      </Card>
    );
  }
}
export default withStyles(EventsListCard.styles)(EventsListCard);

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
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Grid from '@material-ui/core/Grid';
import LinearProgress from '@material-ui/core/LinearProgress';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import moment from 'moment';

class ClientsCard extends Component {
  static styles = {
    root: {
      'min-height': '200px'
    },
    cardContentItem: {
      width: '100%'
    }
  };

  static propTypes = {
    apiClient: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      service: undefined,
      actionPending: false
    };
  }

  handleClients = response => {
    response.body.forEach(function(client) {
      client.properties.modified = moment.utc(client.properties.modified);
    });
    this.setState({
      clients: response.body
    });
    console.log('ClientsCard.handleClients', response.body);
  };

  handleSwitchChange = client => event => {
    client.properties.active = event.target.checked;
    this.setState({ clients: this.state.clients });

    this.props.apiClient.bikebuds.update_client({
      payload: client.properties
    });
  };

  componentDidMount() {
    this.setState({});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ClientsCard.componentDidUpdate', prevProps);
    if (this.props.apiClient && this.state.clients === undefined) {
      console.log('ClientsCard.componentDidUpdate: apiClient and no state');
      this.props.apiClient.bikebuds.get_clients().then(this.handleClients);
    }
  }

  renderCardContent() {
    return (
      <CardContent className={this.props.classes.content}>
        <Grid container direction="column" justify="center" alignItems="center">
          <Grid className={this.props.classes.cardContentItem} item>
            <Typography variant="h5">Receive Notifications</Typography>
            {this.state.clients === undefined ? (
              <LinearProgress />
            ) : (
              <FormControl
                component="fieldset"
                className={this.props.classes.formControl}
              >
                {this.state.clients.map((client, index) => {
                  return (
                    <FormControlLabel
                      key={index}
                      onChange={this.handleSwitchChange(client)}
                      checked={client.properties.active}
                      value={client.properties.token}
                      control={<Switch />}
                      label={
                        client.properties.type
                          ? client.properties.type
                          : client.properties.modified.format('LLL')
                      }
                      labelPlacement="end"
                    />
                  );
                })}
              </FormControl>
            )}
          </Grid>
          <Grid className={this.props.classes.cardContentItem} item></Grid>
        </Grid>
      </CardContent>
    );
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.renderCardContent()}
      </Card>
    );
  }
}
export default withStyles(ClientsCard.styles)(ClientsCard);

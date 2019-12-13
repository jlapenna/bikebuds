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
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import LinearProgress from '@material-ui/core/LinearProgress';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import makeCancelable from 'makecancelable';
import moment from 'moment';

class DevicesFormControl extends Component {
  static styles = createStyles({});

  static propTypes = {
    apiClient: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      service: undefined,
      actionPending: false,
    };
  }

  componentDidMount() {
    this.setState({});
  }

  componentWillUnmount() {
    if (this._cancelGetClients) {
      this._cancelGetClients();
    }
    if (this._cancelUpdateClient) {
      this._cancelUpdateClient();
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.apiClient && !this.state.fetched) {
      this.setState({ fetched: true });
      this._cancelGetClients = makeCancelable(
        this.props.apiClient.bikebuds.get_clients(),
        this.handleClients,
        console.error
      );
    }
  }

  handleClients = response => {
    response.body.forEach(function(client) {
      client.properties.created = moment.utc(client.properties.created);
    });
    this.setState({
      clients: response.body,
    });
  };

  handleSwitchChange = client => event => {
    client.properties.active = event.target.checked;
    this.setState({ clients: this.state.clients });

    this._cancelUpdateClient = makeCancelable(
      this.props.apiClient.bikebuds.update_client({
        payload: client.properties,
      }),
      () => {},
      console.error
    );
  };

  render() {
    return (
      <FormControl
        component="fieldset"
        className={this.props.classes.formControl}
      >
        <Typography variant="h6">Devices</Typography>
        {this.state.clients === undefined ? (
          <LinearProgress />
        ) : (
          <React.Fragment>
            {this.state.clients.map((client, index) => {
              return (
                <FormControlLabel
                  key={index}
                  onChange={this.handleSwitchChange(client)}
                  checked={client.properties.active}
                  value={client.properties.token}
                  control={<Switch />}
                  label={
                    client.properties.created.format('LLL') +
                    ' ' +
                    client.properties.type
                  }
                  labelPlacement="end"
                />
              );
            })}
          </React.Fragment>
        )}
      </FormControl>
    );
  }
}
export default withStyles(DevicesFormControl.styles)(DevicesFormControl);

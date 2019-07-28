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
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormGroup from '@material-ui/core/FormGroup';
import Grid from '@material-ui/core/Grid';
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import cloneDeepWith from 'lodash/cloneDeepWith';

import DevicesFormControl from './DevicesFormControl';

class PreferencesCard extends Component {
  static styles = theme => ({
    root: {
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between'
    }
  });

  static propTypes = {
    profile: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      updatingRemote: false
    };
  }

  handlePreferences = response => {
    this.props.profile.updatePreferences(response.body);
    this.setState({ updatingRemote: false });
  };

  handleNotifChange = event => {
    this.setState({ updatingRemote: true });

    var newPreferences = cloneDeepWith(
      this.props.profile.user.properties.preferences
    );
    newPreferences.daily_weight_notif = event.target.checked;
    this.updatePreferences(newPreferences);
  };

  handleRadioGroupChange = event => {
    this.setState({ updatingRemote: true });

    var newPreferences = cloneDeepWith(
      this.props.profile.user.properties.preferences
    );
    if (event.target.name === 'units') {
      newPreferences.units = event.target.value;
    } else if (event.target.name === 'weight_service') {
      newPreferences.weight_service = event.target.value;
    }
    this.updatePreferences(newPreferences);
  };

  /**
   * Update locally and remote, this will trigger to renders, once for local,
   * once when the result comes back.
   */
  updatePreferences = newPreferences => {
    // Local
    this.props.profile.updatePreferences({ preferences: newPreferences });

    // Remote
    this.props.apiClient.bikebuds
      .update_preferences({ payload: newPreferences })
      .then(this.handlePreferences);
  };

  render() {
    return (
      <Card className={this.props.classes.root}>
        <CardContent className={this.props.classes.content}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={12}>
              <FormControl
                component="fieldset"
                className={this.props.classes.formControl}
                disabled={this.state.updatingRemote}
              >
                <Typography variant="h5">Unit</Typography>
                <RadioGroup
                  aria-label="Measurement Units"
                  name="units"
                  className={this.props.classes.group}
                  value={this.props.profile.user.properties.preferences.units}
                  onChange={this.handleRadioGroupChange}
                >
                  <FormControlLabel
                    value="METRIC"
                    control={<Radio />}
                    label="Metric"
                  />
                  <FormControlLabel
                    value="IMPERIAL"
                    control={<Radio />}
                    label="Imperial"
                  />
                </RadioGroup>
              </FormControl>
              <FormControl
                component="fieldset"
                className={this.props.classes.formControl}
                disabled={this.state.updatingRemote}
              >
                <Typography variant="h5">Weight Service</Typography>
                <RadioGroup
                  aria-label="Weight Service"
                  name="weight_service"
                  className={this.props.classes.group}
                  value={
                    this.props.profile.user.properties.preferences
                      .weight_service
                  }
                  onChange={this.handleRadioGroupChange}
                >
                  <FormControlLabel
                    value="FITBIT"
                    control={<Radio />}
                    label="Fitbit"
                  />
                  <FormControlLabel
                    value="WITHINGS"
                    control={<Radio />}
                    label="Withings"
                  />
                </RadioGroup>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={12}>
              <FormControl
                component="fieldset"
                className={this.props.classes.formControl}
                disabled={this.state.updatingRemote}
              >
                <Typography variant="h5">Notifications</Typography>
                <FormGroup disabled={this.state.updatingRemote}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={
                          this.props.profile.user.properties.preferences
                            .daily_weight_notif
                        }
                        onChange={this.handleNotifChange}
                      />
                    }
                    label="Daily Weight Notification"
                  />
                </FormGroup>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={12}>
              <DevicesFormControl apiClient={this.props.apiClient} />
            </Grid>
          </Grid>
        </CardContent>
        <CardActions />
      </Card>
    );
  }
}
export default withStyles(PreferencesCard.styles)(PreferencesCard);

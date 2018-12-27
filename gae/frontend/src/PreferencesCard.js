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
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';
import Typography from '@material-ui/core/Typography';

import cloneDeepWith from 'lodash/cloneDeepWith';

const styles = theme => ({
  root: {
    "min-height": "200px",
  },
  container: {
    display: 'flex',
    flexWrap: 'wrap',
  },
});

class PreferencesCard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      preferences: undefined,
    }
  }

  onHandleChange = (event) => {
    if (!this.state.preferences) {
      return;
    }
    var newState = {preferences: cloneDeepWith(this.state.preferences)};
    if (event.target.name === 'units') {
      newState.preferences.units = event.target.value;
    } else if (event.target.name === 'weight_service') {
      newState.preferences.weight_service = event.target.value;
    }
    this.setState(newState);
    window.gapi.client.bikebuds.update_preferences(newState).then(this.updatePreferencesState);
  }

  updatePreferencesState = (response) => {
      this.setState({
        preferences: response.result.preferences,
      });
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
    console.log('PreferencesCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.preferences === undefined) {
      window.gapi.client.bikebuds.get_preferences().then(this.updatePreferencesState);
    }
  }

  renderCardContent() {
    if (this.state.preferences) {
      var units = this.state.preferences.units;
      var weight_service = this.state.preferences.weight_service;
    }
    return (
      <CardContent className={this.props.classes.content}>
        <div className={this.props.classes.container}>
          <FormControl component="fieldset" className={this.props.classes.formControl}
            disabled={!this.state.preferences}
          >
            <Typography variant="h5">Unit</Typography>
            <RadioGroup
              aria-label="Measurement System"
              name="units"
              className={this.props.classes.group}
              value={units}
              onChange={this.onHandleChange}
            >
              <FormControlLabel value="METRIC" control={<Radio />} label="Metric" />
              <FormControlLabel value="IMPERIAL" control={<Radio />} label="Imperial" />
            </RadioGroup>
          </FormControl>
          <FormControl component="fieldset" className={this.props.classes.formControl}
            disabled={!this.state.preferences}
          >
            <Typography variant="h5">Weight Service</Typography>
            <RadioGroup
              aria-label="Measurement System"
              name="weight_service"
              className={this.props.classes.group}
              value={weight_service}
              onChange={this.onHandleChange}
            >
              <FormControlLabel value="FITBIT" control={<Radio />} label="Fitbit" />
              <FormControlLabel value="WITHINGS" control={<Radio />} label="Withings" />
            </RadioGroup>
          </FormControl>
        </div>
      </CardContent>
    )
  };

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.renderCardContent()}
        <CardActions>
        </CardActions>
      </Card>
    );
  };
}

export default withStyles(styles)(PreferencesCard);

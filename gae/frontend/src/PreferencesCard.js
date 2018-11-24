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

import cloneDeepWith from 'lodash/cloneDeepWith';

import { withStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormLabel from '@material-ui/core/FormLabel';
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';


const styles = theme => ({
  root: {
    height:300,
  },
  avatar: {
    width: 128,
    height: 128,
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
    var newState = {preferences: cloneDeepWith(this.state.preferences)};
    newState.preferences.units = event.target.value;
    this.setState(newState);
    window.gapi.client.bikebuds.set_preferences(newState).then(this.updatePreferencesState);
  }

  updatePreferencesState = (response) => {
      this.setState({
        preferences: response.result.preferences,
      });
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
    if (this.state.preferences === undefined) {
      return;
    }
    return (
        <CardContent className={this.props.classes.content}>
          <FormControl component="fieldset" className={this.props.classes.formControl}>
            <FormLabel component="legend">Unit</FormLabel>
            <RadioGroup
              aria-label="Measurement System"
              name="units"
              className={this.props.classes.group}
              value={this.state.preferences.units}
              onChange={this.onHandleChange}
            >
              <FormControlLabel value="IMPERIAL" control={<Radio />} label="Imperial" />
              <FormControlLabel value="METRIC" control={<Radio />} label="Metric" />
            </RadioGroup>
          </FormControl>
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

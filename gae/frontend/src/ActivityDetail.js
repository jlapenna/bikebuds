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

const styles = {
  root: {
    min_height: "500px",
  },
  iframe: {
    height: "450px",
    width: "590px",
    border: "0",
  },
};

class ActivityDetail extends Component {

  render() {
    if (this.props.activity === undefined) {
      return (
        <div>&#8203;</div>
      );
    }

    if (!this.props.activity.embed_token) {
      return (
        <div>{this.props.activity.name}</div>
      );
    }

    var embed_url = 'https://www.strava.com/activities/'
      + this.props.activity.id
      + '/embed/'    
      + this.props.activity.embed_token;

    return (
      <div className={this.props.classes.root}>
        <iframe className={this.props.classes.iframe}
          src={embed_url}
          title={this.props.activity.name} />
      </div>
    );
  };
}


ActivityDetail.propTypes = {
  activity: PropTypes.object,
}
export default withStyles(styles)(ActivityDetail);

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

class EventDetail extends Component {
  static styles = {
    root: {
      height: '100%',
      width: '100%',
      overflow: 'visible',
      display: 'flex',
      'flex-direction': 'column',
      'align-items': 'center'
    }
  };

  static propTypes = {
    event: PropTypes.object
  };

  render() {
    if (this.props.event === undefined) {
      return <div className={this.props.classes.root} />;
    }

    return (
      <div className={this.props.classes.root}>{this.props.event.title}</div>
    );
  }
}

export default withStyles(EventDetail.styles)(EventDetail);
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
import React from 'react';

import { Redirect } from 'react-router-dom';

import { withStyles } from '@material-ui/core/styles';

import SignupStepper from './SignupStepper';

class Signup extends React.Component {
  static styles = {
    root: {
      'background-color': 'red',
      display: 'flex',
      height: '100%',
    },
  };

  static propTypes = {
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      stepperFinished: false,
    };
  }

  handleStepperFinished = () => {
    this.setState({
      stepperFinished: true,
    });
  };

  render() {
    if (this.state.stepperFinished) {
      return (
        <Redirect to={{ pathname: '/', search: window.location.search }} />
      );
    }

    return (
      <SignupStepper
        firebase={this.props.firebase}
        firebaseUser={this.props.firebaseUser}
        onFinished={this.handleStepperFinished}
      />
    );
  }
}
export default withStyles(Signup.styles)(Signup);

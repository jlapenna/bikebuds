import React from 'react';
import PropTypes from 'prop-types';

import { Redirect } from "react-router-dom";

import { withStyles } from '@material-ui/core/styles';

import SignupStepper from './SignupStepper';

class Signup extends React.Component {

  static propTypes = {
    firebaseUser: PropTypes.object.isRequired,
  }

  static styles = (theme) => ({
    root: {
      "background-color": 'red',
      display: 'flex',
      height: '100%',
    },
  })

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
  }

  render() {
    if (this.state.stepperFinished) {
      return (
        <Redirect to="/" />
      )
    };

    return (
      <SignupStepper
        firebaseUser={this.props.firebaseUser}
        gapiReady={this.props.gapiReady}
        onFinished={this.handleStepperFinished}
      />
    );
  }
}
export default withStyles(Signup.styles)(Signup);

import React from 'react';
import PropTypes from 'prop-types';

import { Redirect } from "react-router-dom";

import { withStyles } from '@material-ui/core/styles';

import SignupStepper from './SignupStepper';


const styles = (theme) => ({
  root: {
    "background-color": 'red',
    display: 'flex',
    height: '100%',
  },
});

class Signup extends React.Component {
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


Signup.propTypes = {
  firebaseUser: PropTypes.object.isRequired,
};
export default withStyles(styles)(Signup);

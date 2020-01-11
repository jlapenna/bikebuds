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
import React from 'react';

import { createStyles, withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Hidden from '@material-ui/core/Hidden';
import MobileStepper from '@material-ui/core/MobileStepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import KeyboardArrowLeft from '@material-ui/icons/KeyboardArrowLeft';
import KeyboardArrowRight from '@material-ui/icons/KeyboardArrowRight';
import Stepper from '@material-ui/core/Stepper';
import Typography from '@material-ui/core/Typography';

import { config } from './config';
import { createSession } from './session_util';
import Consent from './Consent';
import Privacy from './Privacy';
import ToS from './ToS';

class SignupStepper extends React.Component {
  static styles = theme =>
    createStyles({
      root: {
        height: '100%',
      },
      stepBody: {
        marginTop: theme.spacing(1),
        marginBottom: theme.spacing(1),
      },
      stepContent: {
        marginTop: theme.spacing(1),
        marginBottom: theme.spacing(1),
      },
      stepper: {},
      mobileButton: {
        marginRight: theme.spacing(1),
        marginLeft: theme.spacing(1),
      },
      desktopButton: {
        marginRight: theme.spacing(1),
      },
    });

  static propTypes = {
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
    onFinished: PropTypes.func.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      steps: this.createSteps(),
      activeStepIndex: 0,
      connectTransition: false,
    };
  }

  createSteps = () => {
    return [
      {
        label: 'Welcome, ' + this.props.firebaseUser.displayName,
        content: () => <Consent />,
        isOptional: false,
        buttonLabel: 'I\u00A0Agree',
      },
      {
        label: 'Terms of Service',
        content: () => {
          return <ToS />;
        },
        isOptional: false,
        buttonLabel: 'Next',
      },
      {
        label: 'Privacy',
        content: () => {
          return <Privacy />;
        },
        isOptional: false,
        buttonLabel: 'Next',
      },
      {
        label: 'Connect Strava',
        content: () => {
          return (
            <div>
              Connect your account, we will use your activities and profile.
            </div>
          );
        },
        isOptional: false,
        serviceName: 'strava',
        buttonLabel: 'Connect',
      },
      {
        label: 'Connect Withings',
        content: () => {
          return <div>Connect your account, we will use your health data.</div>;
        },
        isOptional: true,
        serviceName: 'withings',
        buttonLabel: 'Connect',
      },
      {
        label: 'Connect Fitbit',
        content: () => {
          return <div>Connect your account, we will use your health data.</div>;
        },
        isOptional: true,
        serviceName: 'fitbit',
        buttonLabel: 'Connect',
      },
      {
        label: 'Wrap up',
        content: () => {
          return <div>You&apos;re all set!</div>;
        },
        isOptional: false,
        buttonLabel: 'Finish',
      },
    ];
  };

  handleBack = () => {
    this.setState(state => ({
      activeStepIndex: state.activeStepIndex - 1,
    }));
  };

  handleNext = () => {
    const { activeStepIndex } = this.state;
    let activeStep = this.state.steps[activeStepIndex];

    if (activeStep.serviceName !== undefined) {
      this.setState({ connectPending: true });

      createSession(this.props.firebase, response => {
        if (response.status === 200) {
          window.location.replace(
            config.frontendUrl +
              '/services/' +
              activeStep.serviceName +
              '/init?dest=/signup?service=' +
              activeStep.serviceName
          );
        } else {
          console.warn('Unable to create a session.', response);
          this.setState({ connectPending: false });
        }
      });
      return;
    }

    if (activeStepIndex === this.state.steps.length - 1) {
      this.props.onFinished();
    }

    this.setState({
      activeStepIndex: activeStepIndex + 1,
    });
  };

  handleSkip = () => {
    const { activeStepIndex } = this.state;
    let activeStep = this.state.steps[activeStepIndex];
    if (!activeStep.isOptional) {
      // You probably want to guard against something like this,
      // it should never occur unless someone's actively trying to break something.
      throw new Error("You can't skip a step that isn't optional.");
    }

    this.setState(state => {
      return {
        activeStepIndex: state.activeStepIndex + 1,
      };
    });
  };

  componentDidMount() {
    let params = new URLSearchParams(window.location.search);
    if (!!params.get('skipTos')) {
      this.setState({
        activeStepIndex: 3,
      });
    } else {
      let startingService = params.get('service');
      for (var i = 0; i < this.state.steps.length; i++) {
        if (this.state.steps[i].serviceName === startingService) {
          this.setState({
            activeStepIndex: i + 1,
          });
          break;
        }
      }
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.state.activeStepIndex !== prevState.activeStepIndex) {
      window.scrollTo(0, 0);
    }
  }

  renderSteps() {
    return this.state.steps.map((step, index) => {
      const props = {};
      const labelProps = {};
      return (
        <Step key={step.label} {...props}>
          <StepLabel {...labelProps}>{step.label}</StepLabel>
        </Step>
      );
    });
  }

  render() {
    const { classes } = this.props;
    const { steps, activeStepIndex, connectPending } = this.state;

    if (activeStepIndex === steps.length) {
      return null;
    }

    let activeStep = steps[activeStepIndex];
    let stepContent = activeStep ? activeStep.content() : null;

    return (
      <div className={classes.root}>
        <div ref={ref => (this._div = ref)} />
        <Hidden xsDown>
          <div className={classes.stepper}>
            <Stepper alternativeLabel activeStep={activeStepIndex}>
              {this.renderSteps()}
            </Stepper>
          </div>
        </Hidden>
        <div className={classes.stepBody}>
          <Typography variant="h4">{activeStep.label}</Typography>
          <div className={classes.stepContent}>{stepContent}</div>
          <Hidden smUp>
            {activeStep.isOptional && (
              <Button
                disabled={connectPending}
                variant="outlined"
                onClick={this.handleSkip}
                className={classes.button}
              >
                Skip
              </Button>
            )}
          </Hidden>
        </div>
        <Hidden smUp>
          <div className={classes.stepper}>
            <MobileStepper
              variant="progress"
              steps={steps.length}
              activeStep={activeStepIndex}
              nextButton={
                <React.Fragment>
                  <Button
                    className={classes.mobileButton}
                    variant="contained"
                    color="primary"
                    disabled={connectPending}
                    onClick={this.handleNext}
                  >
                    {activeStep.buttonLabel}
                    {this.props.theme.direction === 'rtl' ? (
                      <KeyboardArrowLeft />
                    ) : (
                      <KeyboardArrowRight />
                    )}
                  </Button>
                </React.Fragment>
              }
              backButton={
                <Button
                  disabled={connectPending || this.state.activeStepIndex === 0}
                  className={classes.mobileButton}
                  variant="outlined"
                  color="primary"
                  onClick={this.handleBack}
                >
                  {this.props.theme.direction === 'rtl' ? (
                    <KeyboardArrowRight />
                  ) : (
                    <KeyboardArrowLeft />
                  )}
                  Back
                </Button>
              }
            >
              {this.renderSteps()}
            </MobileStepper>
          </div>
        </Hidden>
        <Hidden xsDown>
          <Button
            disabled={connectPending || this.state.activeStepIndex === 0}
            onClick={this.handleBack}
            className={classes.desktopButton}
          >
            Back
          </Button>
          {activeStep.isOptional && (
            <Button
              disabled={connectPending}
              variant="outlined"
              color="primary"
              onClick={this.handleSkip}
              className={classes.desktopButton}
            >
              Skip
            </Button>
          )}
          <Button
            disabled={connectPending}
            variant="contained"
            color="primary"
            onClick={this.handleNext}
            className={classes.desktopButton}
          >
            {activeStep.buttonLabel}
          </Button>
        </Hidden>
      </div>
    );
  }
}
export default withStyles(SignupStepper.styles, { withTheme: true })(
  SignupStepper
);

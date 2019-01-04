import React from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Hidden from '@material-ui/core/Hidden';
import MobileStepper from '@material-ui/core/MobileStepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import KeyboardArrowLeft from '@material-ui/icons/KeyboardArrowLeft';
import KeyboardArrowRight from '@material-ui/icons/KeyboardArrowRight';
import Stepper from '@material-ui/core/Stepper';
import Typography from '@material-ui/core/Typography';

import { config } from './Config';
import { createSession } from './session_util';

const styles = (theme) => ({
  root: {
    height: '100%',
  },
  stepBody: {
    marginTop: theme.spacing.unit,
    marginBottom: theme.spacing.unit,
  },
  stepContent: {
    marginTop: theme.spacing.unit,
    marginBottom: theme.spacing.unit,
  },
  stepFooter: {
  },
  mobileButton: {
    marginRight: theme.spacing.unit,
    marginLeft: theme.spacing.unit,
  },
  desktopButton: {
    marginRight: theme.spacing.unit,
  },
});



class SignupStepper extends React.Component {
  static propTypes = {
    classes: PropTypes.object,
    firebaseUser: PropTypes.object.isRequired,
    gapiReady: PropTypes.bool.isRequired,
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
        label: 'Welcome',
        content: () => {
          return (
            <React.Fragment>
              This may be your first visit or updates may have triggered a
              profile update. In either case, step through this wizard to get
              your account set up properly.
            </React.Fragment>
          );
        },
        isOptional: false,
        buttonLabel: 'Next',
      },
      {
        label: 'Consent and Notice',
        content: () => {
          return (
            <React.Fragment>
              <div>
                We will:
                <ul>
                  <li><strong>Collect</strong> your data from several third-party services.</li>
                  <li><strong>Share</strong> your data with other users of bikebuds and its administrators.</li>
                </ul>
                <div>
                  Though efforts are made to maintain the privacy and access controls
                  offered by the third-party services, the nature of this service requires
                  that these privacy controls and restrictions are ignored.
                  <p />
                  <em>This is not an officially supported Google product.</em>
                </div>
              </div>
            </React.Fragment>
          );
        },
        isOptional: false,
        buttonLabel: 'Next',
      },
      {
        label: 'Connect Strava',
        content: () => {
          return (
            <div>Connect your account, we will use your activities and profile.</div>
          );
        },
        isOptional: true,
        serviceName: 'strava',
        buttonLabel: 'Connect',
      },
      {
        label: 'Connect Withings',
        content: () => {
          return (
            <div>Connect your account, we will use your health data.</div>
          );
        },
        isOptional: true,
        serviceName: 'withings',
        buttonLabel: 'Connect',
      },
      {
        label: 'Connect Fitbit',
        content: () => {
          return (
            <div>Connect your account, we will use your health data.</div>
          );
        },
        isOptional: true,
        serviceName: 'fitbit',
        buttonLabel: 'Connect',
      },
      {
        label: 'Wrap up',
        content: () => {
          return (
            <div>You&apos;re all set!</div>
          );
        },
        isOptional: false,
        buttonLabel: 'Finish',
      },
    ];
  }

  handleNext = () => {
    const { activeStepIndex } = this.state;
    let activeStep = this.state.steps[activeStepIndex];

    if (activeStep.serviceName !== undefined) {
      this.setState({connectPending: true});

      createSession((response) => {
        if (response.status === 200) {
          window.location.replace(config.frontendUrl + '/services/' +
            activeStep.serviceName + '/init?dest=/signup?service=' + activeStep.serviceName);
        } else {
          console.log('Unable to create a session.', response);
          this.setState({connectPending: false});
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

  handleBack = () => {
    this.setState(state => ({
      activeStepIndex: state.activeStepIndex - 1,
    }));
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

  /**
   * @inheritDoc
   */
  componentDidMount() {
    let params = new URLSearchParams(window.location.search);
    let startingService = params.get('service');
    for (var i = 0; i < this.state.steps.length; i++) {
      if (this.state.steps[i].serviceName === startingService) {
        this.setState({
          activeStepIndex: (i + 1),
        });
        break;
      }
    }
  }

  renderSteps() {
    return this.state.steps.map((step, index) => {
      const props = {};
      const labelProps = {};
      if (step.isOptional) {
        labelProps.optional = <Typography variant="caption">Optional</Typography>;
      }
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
    };

    let activeStep = steps[activeStepIndex];
    let stepContent = activeStep ? activeStep.content(this.props) : null;

    return (
      <div className={classes.root}>
        <div className={classes.stepBody}>
          <Typography variant="h4">{activeStep.label}</Typography>
          <div className={classes.stepContent}>
            {stepContent}
          </div>
          <Hidden smUp implementation="css">
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
        <div className={classes.stepFooter}>
          <Hidden xsDown implementation="css">
            <Stepper
              alternativeLabel
              activeStep={activeStepIndex}
            >
              {this.renderSteps()}
            </Stepper>
          </Hidden>
          <Hidden smUp implementation="css">
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
                  {this.props.theme.direction === 'rtl' ? <KeyboardArrowLeft /> : <KeyboardArrowRight />}
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
                  {this.props.theme.direction === 'rtl' ? <KeyboardArrowRight /> : <KeyboardArrowLeft />}
                  Back

                </Button>
              }
            >
              {this.renderSteps()}
            </MobileStepper>
          </Hidden>
          <Hidden xsDown implementation="css">
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
      </div>
    );
  }
}

export default withStyles(styles, { withTheme: true })(SignupStepper);

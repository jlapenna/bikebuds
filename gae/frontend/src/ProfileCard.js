import React, { Component } from 'react';

import firebase from 'firebase/app';
import 'firebase/auth';

import { withStyles } from '@material-ui/core/styles';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import { backendConfig } from './Config';

const styles = {
  root: {
    minWidth: 275,
    maxWidth: 375,
  },
  avatar: {
    width: 60,
    height: 60,
  }
};

class ProfileCard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      profile: undefined,
    }
    this.onSignOut = this.onSignOut.bind(this);
    this.onConnectServices = this.onConnectServices.bind(this);
  }

  onSignOut() {
    firebase.auth().signOut().then(() => {
      window.location.reload();
    });
  };

  onConnectServices() {
    firebase.auth().currentUser.getIdToken().then((idToken) => {
      fetch(backendConfig.backendHostUrl + '/create_session', {
        /* Set header for the XMLHttpRequest to get data from the web server
         * associated with userIdToken */
        headers: {
          'Authorization': 'Bearer ' + idToken
        },
        method: 'POST',
        credentials: 'include'
      }).then((response) => {
        if (response.status === 200) {
          window.location.replace(backendConfig.backendHostUrl + '/signup');
        } else {
          console.log('Unable to create a session.', response);
        }
      });
    });
  };

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ProfileCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.profile === undefined) {
      console.log('ProfileCard.componentDidUpdate: user');
      window.gapi.client.bikebuds.get_profile().then((response) => {
        this.setState({profile: response.result,
                       created: new Date(response.result.created).toLocaleDateString(),
                      });
        console.log('ProfileCard.setState: profile: ', response.result);
      });
    }
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        <CardContent className={this.props.classes.content}>
          <Grid container
                direction="column"
                justify="center"
                alignItems="center">
            <Avatar className={this.props.classes.avatar}
                    alt={this.props.firebaseUser.displayName}
                    src={this.props.firebaseUser.photoURL}>
            </Avatar>
            <Typography variant="h5">{this.props.firebaseUser.displayName}</Typography>
            {this.state.profile &&
                <i>Joined {this.state.created}</i>
            }
            {!this.state.profile &&
                <i>&#8203;</i>
            }
          </Grid>
        </CardContent>
        <CardActions>
          <Button color="primary" variant="contained"
              onClick={this.onConnectServices}>Connect Services</Button>
          <Button color="secondary"
              onClick={this.onSignOut}>Sign-out</Button>
        </CardActions>
      </Card>
    );
  };
}

export default withStyles(styles)(ProfileCard);

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
      response: undefined,
    }
    this.onSignOut = this.onSignOut.bind(this);
  }

  onSignOut() {
    firebase.auth().signOut().then(() => {
      window.location.reload();
    });
  };

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ProfileCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.response === undefined) {
      console.log('ProfileCard.componentDidUpdate: get_user');
      window.gapi.client.bikebuds.get_user().then((response) => {
        this.setState({response: response.body});
        console.log('ProfileCard.setState: response: ', response);
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
            <Typography variant="h6">{this.state.response}</Typography>
          </Grid>
        </CardContent>
        <CardActions>
          <Button color="secondary"
              onClick={this.onSignOut}>Sign-out</Button>
        </CardActions>
      </Card>
    );
  };
}

export default withStyles(styles)(ProfileCard);

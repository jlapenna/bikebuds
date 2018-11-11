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

class ServiceCard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      service: undefined,
    }
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ServiceCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.service === undefined) {
      console.log('ServiceCard.componentDidUpdate: user');
      window.gapi.client.bikebuds.get_service().then((response) => {
        this.setState({service: response.result,
                       created: new Date(response.result.created).toLocaleDateString(),
                       modified: new Date(response.result.modified).toLocaleDateString(),
                      });
        console.log('ServiceCard.setState: service: ', response.result);
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
            <Typography variant="h5">{this.props.serviceName}</Typography>
            {this.state.service &&
                <i>Updated {this.state.modified}</i>
            }
            {!this.state.service &&
                <i>&#8203;</i>
            }
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

export default withStyles(styles)(ServiceCard);

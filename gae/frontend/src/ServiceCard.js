import React, { Component } from 'react';

import firebase from 'firebase/app';
import 'firebase/auth';

import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import { backendConfig } from './Config';


const styles = {
  root: {
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
      syncActionPending: false,
      connectActionPending: false,

    }
    this.onConnect = this.onConnect.bind(this);
    this.onSync = this.onSync.bind(this);
    this.updateServiceState = this.updateServiceState.bind(this);
  }

  onConnect() {
    this.setState({connectActionPending: true});
    if (this.state.connected !== undefined && this.state.connected) {
      window.gapi.client.bikebuds.disconnect_service(
        {'id': this.props.serviceName}).then((response) => {
          this.updateServiceState(response);
          this.setState({connectActionPending: false});
        });
      return;
    }
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
          console.log(backendConfig.backendHostUrl + '/'
            + this.props.serviceName + '/init?dest=/frontend');
          window.location.replace(backendConfig.backendHostUrl + '/'
            + this.props.serviceName + '/init?dest=/frontend');
        } else {
          console.log('Unable to create a session.', response);
          this.setState({connectActionPending: false});
        }
      });
    });
  }

  onSync() {
    this.setState({syncActionPending: true});
  }

  updateServiceState(response) {
    this.setState({
      service: response.result,
      created: new Date(response.result.created).toLocaleDateString(),
      modified: new Date(response.result.modified).toLocaleDateString(),
      connected: response.result.connected,
    });
    console.log('ServiceCard.setState: service: ', response.result);
  }

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('ServiceCard.componentDidUpdate', prevProps);
    if (this.props.gapiReady && this.state.service === undefined) {
      window.gapi.client.bikebuds.get_service(
        {'id': this.props.serviceName}).then(this.updateServiceState);
    }
  }

  renderCardContent() {
    if (this.state.service === undefined) {
      return;
    }
    return (
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
    )
  };

  renderCardActions() {
    if (this.state.service === undefined) {
      return;
    }
    if (this.state.connected) {
      return (
        <CardActions>
          <Button color="primary" variant="contained"
            disabled={this.state.syncActionPending}
            onClick={this.onSync}>Sync
            {this.state.syncActionPending && <CircularProgress size={20} />}
          </Button>
          <Button color="secondary"
            disabled={this.state.connectActionPending}
            onClick={this.onConnect}>Disconnect
            {this.state.connectActionPending && <CircularProgress size={20} />}
          </Button>
        </CardActions>
      )
    } else {
      return (
        <CardActions>
          <Button color="primary" variant="contained"
            disabled={this.state.connectActionPending}
            onClick={this.onConnect}>Connect
            {this.state.connectActionPending && <CircularProgress size={20} />}
          </Button>
        </CardActions>
      )
    }
  }

  render() {
    return (
      <Card className={this.props.classes.root}>
        {this.renderCardContent()}
        {this.renderCardActions()}
      </Card>
    );
  };
}

export default withStyles(styles)(ServiceCard);

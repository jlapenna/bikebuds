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
import React, { Component } from 'react';

import { createStyles, withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import Grid from '@material-ui/core/Grid';

import makeCancelable from 'makecancelable';
import JSONPretty from 'react-json-pretty';

class AdminUsers extends Component {
  static styles = createStyles({});

  static propTypes = {
    adminApi: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      actionPending: false,
      dialogOpen: false,
      bot: undefined,
      deleteUserSub: '',
    };
  }

  componentDidMount() {
    this.setState({});
  }

  componentWillUnmount() {
    if (this._cancelDeleteUser) {
      this._cancelDeleteUser();
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.adminApi && this.state.users === undefined) {
      this.setState({ users: null });
      this.props.adminApi
        .get_users()
        .then(response => this.setState({ users: response }));
    }
  }

  handleDeleteUser = key => {
    this._cancelDeleteUser = makeCancelable(
      this.props.adminApi.delete({ payload: key }),
      response => this.setState({ actionPending: false })
    );
  };

  render() {
    return (
      <Grid container spacing={3}>
        {this.state.users &&
          this.state.users.body.map((user, index) => {
            return (
              <Grid item key={index}>
              <Card key={index}>
                <CardHeader title={"User: " + user.user.key.path[0].name} />
                <CardContent>
                  <JSONPretty id="json-pretty" data={user}></JSONPretty>
                </CardContent>
      <CardActions>
        <form noValidate autoComplete="off" onSubmit={this.handleDeleteUser}>
        <Button
          color="primary"
          variant="contained"
          disabled={this.state.actionPending}
          onClick={() => this.handleDeleteUser(user.user.key)}
        >
          Delete User
        </Button>
      </form>
      </CardActions>
              </Card>
              </Grid>
            );
          })}
      </Grid>
    );
  }
}
export default withStyles(AdminUsers.styles)(AdminUsers);

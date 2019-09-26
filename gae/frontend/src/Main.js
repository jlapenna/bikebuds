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

import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import Chrome from './Chrome';
import FcmManager from './FcmManager';
import MainContent from './MainContent';
import ProfileWrapper, { ProfileState } from './ProfileWrapper';
import SwagWrapper from './SwagWrapper';

class Main extends Component {
  static styles = theme => ({
    root: {
      display: 'flex',
    },
    main: {
      height: '100%',
      width: '100%',
      padding: theme.spacing(2),
    },
    mainContent: {
      height: '100%',
      width: '100%',
    },
    spinnerContainer: {
      minHeight: '100vh',
    },
  });

  static propTypes = {
    embed: PropTypes.bool.isRequired,
    match: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
    firebaseToken: PropTypes.string.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      apiClient: null,
      profile: new ProfileState(this.handleProfileUpdated),
    };
  }

  handleSwagReady = client => {
    this.setState({
      apiClient: client.apis,
    });
  };

  handleProfileUpdated = profile => {
    this.setState({
      profile: profile,
    });
  };

  handleFcmMessage = payload => {
    console.log('Main.handleFcmMessage', payload);
  };

  renderMainContent() {
    var mainContent = (
      <MainContent
        className={this.props.classes.mainContent}
        match={this.props.match}
        firebase={this.props.firebase}
        firebaseUser={this.props.firebaseUser}
        apiClient={this.state.apiClient}
        profile={this.state.profile}
      />
    );
    if (this.props.embed) {
      return <div className={this.props.classes.main}>{mainContent}</div>;
    } else {
      return <Chrome profile={this.state.profile} children={mainContent} />;
    }
  }

  renderSpinner() {
    return (
      <Grid
        className={this.props.classes.spinnerContainer}
        container
        spacing={0}
        direction="column"
        alignItems="center"
        justify="center"
      >
        <Grid item>
          <CircularProgress />
        </Grid>
      </Grid>
    );
  }

  render() {
    return (
      <div className={this.props.classes.root}>
        <SwagWrapper
          firebaseUser={this.props.firebaseUser}
          firebaseToken={this.props.firebaseToken}
          onReady={this.handleSwagReady}
        />
        {this.state.apiClient && (
          <ProfileWrapper
            apiClient={this.state.apiClient}
            profile={this.state.profile}
          />
        )}
        {!this.props.embed && this.state.apiClient && (
          <FcmManager
            firebase={this.props.firebase}
            apiClient={this.state.apiClient}
            onMessage={this.handleFcmMessage}
          />
        )}
        {this.state.profile.fetched
          ? this.renderMainContent()
          : this.renderSpinner()}
      </div>
    );
  }
}
export default withStyles(Main.styles, { withTheme: true })(Main);

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

import Chrome from './Chrome';
import FcmManager from './FcmManager';
import MainContent from './MainContent';
import ProfileWrapper, { ProfileState } from './ProfileWrapper';
import SwagWrapper from './SwagWrapper';

class _EmbedChrome extends Component {
  static styles = theme => ({
    root: {
      height: '100%',
      width: '100%',
      padding: theme.spacing(2),
    },
  });

  render() {
    return (
      <main className={this.props.classes.root}>{this.props.children}</main>
    );
  }
}
const EmbedChrome = withStyles(_EmbedChrome.styles)(_EmbedChrome);

class Main extends Component {
  static styles = theme => ({
    root: {
      display: 'flex',
      height: '100%',
      width: '100%',
    },
    main: {
      height: '100%',
      width: '100%',
    },
    mainContent: {
      height: '100%',
      width: '100%',
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

  render() {
    const mainContent = (
      <MainContent
        className={this.props.classes.mainContent}
        match={this.props.match}
        firebase={this.props.firebase}
        firebaseUser={this.props.firebaseUser}
        apiClient={this.state.apiClient}
        profile={this.state.profile}
      />
    );

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
            match={this.props.match}
            profileState={this.state.profile}
          />
        )}
        {!this.props.embed && this.state.apiClient && (
          <FcmManager
            firebase={this.props.firebase}
            apiClient={this.state.apiClient}
            onMessage={this.handleFcmMessage}
          />
        )}
        {this.props.embed ? (
          <EmbedChrome profile={this.state.profile}>{mainContent}</EmbedChrome>
        ) : (
          <Chrome profile={this.state.profile}>{mainContent}</Chrome>
        )}
      </div>
    );
  }
}
export default withStyles(Main.styles, { withTheme: true })(Main);

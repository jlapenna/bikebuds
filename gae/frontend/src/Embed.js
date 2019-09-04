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

import MainContent from './MainContent';
import ProfileWrapper, { ProfileState } from './ProfileWrapper';
import SwagWrapper from './SwagWrapper';

class Embed extends Component {
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
  });

  static propTypes = {
    match: PropTypes.object.isRequired,
    firebase: PropTypes.object.isRequired,
    firebaseUser: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      mobileOpen: false,
      apiClient: null,
      profile: new ProfileState(this.handleProfileUpdated),
      swagClient: null,
    };
  }

  handleSwagReady = client => {
    console.log('Embed.handleSwagReady: ', client);
    this.setState({
      apiClient: client.apis,
    });
  };

  handleSwagFailed = () => {
    console.log('Embed.handleSwagFailed');
    this.setState({
      apiClient: undefined,
    });
  };

  handleProfileUpdated = profile => {
    console.log('Embed.handleProfileUpdated', profile);
    this.setState({
      profile: profile,
    });
  };

  render() {
    return (
      <div className={this.props.classes.root}>
        <SwagWrapper
          onReady={this.handleSwagReady}
          onFailed={this.handleSwagFailed}
        />
        {this.state.apiClient && (
          <ProfileWrapper
            apiClient={this.state.apiClient}
            profile={this.state.profile}
          />
        )}
        <main className={this.props.classes.main}>
          <div className={this.props.classes.toolbar} />
          {this.state.apiClient && (
            <MainContent
              className={this.props.classes.mainContent}
              match={this.props.match}
              firebase={this.props.firebase}
              firebaseUser={this.props.firebaseUser}
              apiClient={this.state.apiClient}
              profile={this.state.profile}
            />
          )}
        </main>
      </div>
    );
  }
}
export default withStyles(Embed.styles, { withTheme: true })(Embed);

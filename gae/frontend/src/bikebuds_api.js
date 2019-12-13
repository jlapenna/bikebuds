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
import React, { Component } from 'react';

import makeCancelable from 'makecancelable';

class BikebudsFetcher extends Component {
  static propTypes = {
    fetcher: PropTypes.func.isRequired,
    params: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      fetched: false,
      response: undefined,
    };
  }

  handleUpdateRequestState = response => {
    this.setState({
      response: response,
    });
  };

  componentDidMount() {
    // Triggers componentDidUpdate on mount.
    this.setState({});
  }

  componentWillUnmount() {
    if (this._cancelFetcher) {
      this._cancelFetcher();
    }
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (prevProps.fetcher !== this.props.fetcher) {
      this.setState({ fetched: false });
    }
    if (this.props.fetcher && !this.state.fetched) {
      this.setState({ fetched: true });
      this._cancelFetcher = makeCancelable(
        this.props.fetcher(this.props.params),
        this.handleUpdateRequestState,
        console.error
      );
    }
  }

  render() {
    return (
      <div className="BikebudsFetcher">{this.props.render(this.state)}</div>
    );
  }
}
export default BikebudsFetcher;

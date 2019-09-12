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

import React, { Component } from 'react';

const defaultMockClient = undefined;
var mockClient = defaultMockClient;

class SwagWrapper extends Component {
  componentDidMount() {
    console.log('SwagWrapper.Mock: Loaded client: ', mockClient);
    this.setState({ clientLoaded: true, client: mockClient });
    this.props.onReady(mockClient);
  }

  render() {
    return <div className="SwagWrapper" />;
  }
}
export default SwagWrapper;

export function __setMockClient(client) {
  mockClient = client;
}

export function __reset() {
  mockClient = defaultMockClient;
}

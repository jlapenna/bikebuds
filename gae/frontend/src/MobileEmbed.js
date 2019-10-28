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
import { Component } from 'react';

export const MobileEmbedEventChannel = window.MobileEmbedEventChannel;

export class MobileEmbedJsController extends Component {
  static propTypes = {
    history: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      target: null,
    };
  }

  doSomething = () => {
    console.log('MobileEmbedJsController: doSomething');
  };

  navigate = dest => {
    console.log('MobileEmbedJsController: navigate:', dest);
    this.props.history.push(dest);
    this.setState({ target: dest });
  };

  componentDidMount() {
    var mobileEmbed = {
      doSomething: this.doSomething,
      navigate: this.navigate,
    };
    window.MobileEmbed = mobileEmbed;
  }

  render() {
    return null;
  }
}

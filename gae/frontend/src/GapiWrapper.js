import React, { Component } from 'react';

import { backendConfig } from './Config';

const bikebudsDiscoveryUrl = backendConfig.apiHostUrl + '/bikebuds-v1.discovery';

class GapiWrapper extends Component {
  constructor(props) {
    super(props);
    this.state = {
      gapiLoaded: false,
      clientLoaded: false,
      bikebudsDiscovery: undefined,
      bikebudsLoaded: undefined,
    }
    this.onGapiLoaded = this.onGapiLoaded.bind(this);
  }

  /** Load the gapi client after the library is loaded. */
  onGapiLoaded() {
    this.setState({gapiLoaded: true});
    window.gapi.load('client', () => {
      console.log('GapiWrapper.onClientLoaded', window.gapi.client);
      this.setState({clientLoaded: true});
    });
  }

  /** Store the discoveryJson after it is loaded. */
  onBikebudsLoaded() {
    console.log('GapiWrapper.onBikebudsLoaded');
    this.setState({bikebudsLoaded: true});
  }

  /**
   * @inheritDoc
   */
  componentDidMount() {
    console.log('GapiWrapper.componentDidMount');

    // Load up the google-api library and a client.
    const gapiScript = document.createElement('script');
    gapiScript.src = 'https://apis.google.com/js/api.js?onload=onGapiLoaded';
    window.onGapiLoaded = this.onGapiLoaded;
    document.body.appendChild(gapiScript)

    // Fetch a discovery doc.
    fetch(bikebudsDiscoveryUrl).then((discoveryResponse) => {
      console.log('GapiWrapper.onDiscoveryFetched', discoveryResponse);
      discoveryResponse.json().then((bikebudsDiscovery) => {
        console.log('GapiWrapper.onDiscoveryLoaded', bikebudsDiscovery);
        this.setState({bikebudsDiscovery: bikebudsDiscovery});
      });
    });
  };

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('GapiWrapper.componentDidUpdate', prevState, this.state);
    if ((this.state.clientLoaded !== prevState.clientLoaded)
      || (this.state.bikebudsDiscovery !== prevState.bikebudsDiscovery)) {
      if (this.state.clientLoaded
        && this.state.bikebudsDiscovery !== undefined
        && this.bikebudsLoaded === undefined) {
        this.setState({bikebudsLoaded: false});
        window.gapi.client.load(this.state.bikebudsDiscovery).then(() => {
          console.log('GapiWrapper.componentDidUpdate: bikebuds', window.gapi.client.bikebuds);
          this.setState({bikebudsLoaded: true});
        });
      }
    }
  };

  /*
  function initJsClient(bikebudsDiscovery) {
    gapi.client.load(bikebudsDiscovery).then(function () {
      console.log("initJsClient: bikebuds", gapi.client.bikebuds);
      firebase.auth().currentUser.getIdToken(true).then(function (idToken) {
        console.log("initJsClient: idToken", idToken);
        var tokenDict = {access_token: idToken};
        gapi.client.setToken(tokenDict);
        gapi.client.setApiKey(config.apiKey);
        gapi.client.bikebuds.get_user().then(
          function(response) {
            console.log('initJsClient: get_user response', response);
          });
      });
    });
  }
  */

  /**
   * @inheritDoc
   */
  render() {
    return (
      <div className="GapiWrapper" />
    );
  };
}

export default GapiWrapper;

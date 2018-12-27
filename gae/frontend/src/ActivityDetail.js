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

import { withScriptjs, withGoogleMap, GoogleMap, Polyline } from 'react-google-maps'

import { config } from './Config'

const styles = {
  root: {
    min_height: "500px",
  },
  iframe: {
    height: "450px",
    width: "590px",
    border: "0",
  },
};

/*
      path={[
        { lat: props.activity.start_latlng.latitude, lng: props.activity.start_latlng.longitude },
        { lat: props.activity.end_latlng.latitude, lng: props.activity.end_latlng.longitude }
      ]}
*/

const googleMapURL = "https://maps.googleapis.com/maps/api/js?key="
  + config.mapsApiKey
  + "&v=3.exp&libraries=geometry,drawing,places";


/*
const MyMapComponent = withScriptjs(withGoogleMap((props) =>
  <GoogleMap
    defaultZoom={10}
  >
    <Polyline
      path={window.google.maps.geometry.encoding.decodePath(props.activity.map.summary_polyline)}
      visible
      options={{
        strokeColor: '#00ffff',
        strokeOpacity: 1,
        strokeWeight: 2,
      }}
    />
  </GoogleMap>
))
*/

const GoogleMapsWrapper = withScriptjs(withGoogleMap(props => {
  const {onMapMounted, ...otherProps} = props;
  return <GoogleMap {...otherProps} ref={c => {
    onMapMounted && onMapMounted(c)
  }}>{props.children}</GoogleMap>
}));


class MyMap extends React.Component {

  state = {
    mapMounted: false,
  };

  _mapRef = null;

  _handleMapMounted = (c) => {
    if (!c || this._mapRef) return;
    this._mapRef = c;

    this.setState({
      mapMounted: true
    });
  };

  /**
   * @inheritDoc
   */
  componentDidUpdate(prevProps, prevState, snapshot) {
    if (!this.state.mapMounted || !this.props.activity) {
      return;
    }
    if (this.state.mapMounted !== prevState.mapMounted
        || this.props.activity !== prevProps.activity) {
      var decodedPolyline = [];
      if (this.props.activity.map.summary_polyline) {
        decodedPolyline = window.google.maps.geometry.encoding.decodePath(
          this.props.activity.map.summary_polyline)
      }

      var bounds = new window.google.maps.LatLngBounds();
      decodedPolyline.forEach((point) => {
        bounds.extend(point);
      });
      this._mapRef.fitBounds(bounds);

      this.setState({
        decodedPolyline: decodedPolyline,
        bounds: bounds
      });
    }
  }

  render() {
    return (
      <GoogleMapsWrapper
        googleMapURL={googleMapURL}
        loadingElement={<div style={{height: `100%`}}/>}
        containerElement={<div style={{height: `100%`}}/>}
        mapElement={<div style={{height: `100%`}}/>}
        defaultZoom={10}
        onMapMounted={this._handleMapMounted}
      >
        <Polyline
          path={this.state.decodedPolyline}
          visible
          options={{
            strokeColor: '#00ffff',
            strokeOpacity: 1,
            strokeWeight: 2,
          }}
        />
      </GoogleMapsWrapper>
    )
  }
}

class ActivityDetail extends Component {

  render() {
    return (
      <MyMap activity={this.props.activity} />
    );
  };
}


ActivityDetail.propTypes = {
  activity: PropTypes.object,
}
export default withStyles(styles)(ActivityDetail);

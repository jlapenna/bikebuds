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
import Hidden from '@material-ui/core/Hidden';
import Typography from '@material-ui/core/Typography';

import {
  withScriptjs,
  withGoogleMap,
  BicyclingLayer,
  GoogleMap,
  Polyline
} from 'react-google-maps';

import { config } from './config';
import { readableDistance, readableDuration, readableSpeed } from './convert';

/*
  path={[
    { lat: props.activity.properties.start_latlng.latitude, lng: props.activity.properties.start_latlng.longitude },
    { lat: props.activity.properties.end_latlng.latitude, lng: props.activity.properties.end_latlng.longitude }
  ]}
*/

const googleMapURL =
  'https://maps.googleapis.com/maps/api/js?key=' +
  config.mapsApiKey +
  '&v=3.exp&libraries=geometry,drawing,places';

const GoogleMapsWrapper = withScriptjs(
  withGoogleMap(props => {
    const { onMapMounted, ...otherProps } = props;
    return (
      <GoogleMap
        {...otherProps}
        ref={c => {
          onMapMounted && onMapMounted(c);
        }}
      >
        {props.children}
      </GoogleMap>
    );
  })
);

class _ActivityMap extends Component {
  static styles = {
    root: {
      height: '100%',
      width: '100%',
      overflow: 'visible',
      display: 'flex',
      'flex-direction': 'column',
      'align-items': 'center'
    },
    containerElement: {
      'min-height': '200px',
      height: '100%',
      width: '100%',
      flex: '1'
    },
    mapElement: {
      height: '100%',
      width: '100%'
    },
    loadingElement: {
      height: '100%',
      width: '100%'
    }
  };

  state = {
    mapMounted: false
  };

  _mapRef = null;

  _handleMapMounted = c => {
    if (!c || this._mapRef) return;
    this._mapRef = c;

    this.setState({
      mapMounted: true
    });
  };

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (!this.state.mapMounted || !this.props.activity) {
      return;
    }
    if (
      this.state.mapMounted !== prevState.mapMounted ||
      this.props.activity !== prevProps.activity
    ) {
      var decodedPolyline = [];
      if (this.props.activity.properties.map.summary_polyline) {
        decodedPolyline = window.google.maps.geometry.encoding.decodePath(
          this.props.activity.properties.map.summary_polyline
        );
      }

      var bounds = new window.google.maps.LatLngBounds();
      decodedPolyline.forEach(point => {
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
    console.log('ActivityMap.render', this.props);
    return (
      <GoogleMapsWrapper
        googleMapURL={googleMapURL}
        loadingElement={<div className={this.props.classes.loadingElement} />}
        containerElement={
          <div className={this.props.classes.containerElement} />
        }
        mapElement={<div className={this.props.classes.mapElement} />}
        defaultZoom={10}
        onMapMounted={this._handleMapMounted}
      >
        <Polyline
          path={this.state.decodedPolyline}
          visible
          options={{
            strokeColor: '#ff4081',
            strokeOpacity: 1,
            strokeWeight: 3
          }}
        />
        <BicyclingLayer autoUpdate />
      </GoogleMapsWrapper>
    );
  }
}
const ActivityMap = withStyles(_ActivityMap.styles)(_ActivityMap);

class ActivityDetail extends Component {
  static styles = {
    root: {
      height: '100%',
      width: '100%',
      overflow: 'visible',
      display: 'flex',
      'flex-direction': 'column',
      'align-items': 'center'
    },
    activityRow: {
      width: '100%'
    },
    activitySummary: {
      width: '100%',
      display: 'flex',
      'align-items': 'stretch'
    },
    activitySummaryItem: {
      width: '100%'
    }
  };

  static propTypes = {
    profile: PropTypes.object,
    activity: PropTypes.object
  };

  render() {
    if (this.props.activity === undefined) {
      return (
        <div className={this.props.classes.root}>
          <div className={this.props.classes.activityRow} />
          <ActivityMap activity={this.props.activity} />
        </div>
      );
    }

    const distance = readableDistance(
      this.props.activity.properties.distance,
      this.props.profile
    );
    const duration = readableDuration(
      this.props.activity.properties.moving_time
    );
    const average_speed = readableSpeed(
      this.props.activity.properties.average_speed,
      this.props.profile
    );
    return (
      <div className={this.props.classes.root}>
        <div className={this.props.classes.activityRow}>
          <div className={this.props.classes.activitySummary}>
            <div className={this.props.classes.activitySummaryItem}>
              <Typography variant="subtitle1">Distance</Typography>
              <Typography variant="h4">{distance}</Typography>
            </div>
            <div className={this.props.classes.activitySummaryItem}>
              <Typography variant="subtitle1">Speed</Typography>
              <Typography variant="h4">{average_speed}</Typography>
            </div>
            <div className={this.props.classes.activitySummaryItem}>
              <Typography variant="subtitle1">Moving Time</Typography>
              <Typography variant="h4">{duration}</Typography>
            </div>
            <Hidden mdDown>
              <div className={this.props.classes.activitySummaryItem}>
                <Typography variant="subtitle1">Calories</Typography>
                <Typography variant="h4">
                  {this.props.activity.properties.kilojoules}
                </Typography>
              </div>
            </Hidden>
          </div>
        </div>
        <ActivityMap activity={this.props.activity} />
      </div>
    );
  }
}

export default withStyles(ActivityDetail.styles)(ActivityDetail);

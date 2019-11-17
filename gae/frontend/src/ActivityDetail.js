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
import Hidden from '@material-ui/core/Hidden';
import Typography from '@material-ui/core/Typography';
import {
  BicyclingLayer,
  GoogleMap,
  LoadScript,
  Polyline,
} from '@react-google-maps/api';

import { config } from './config';
import { readableDistance, readableDuration, readableSpeed } from './convert';

const MAP_LIBRARIES = ['geometry'];

class _ActivityMap extends Component {
  static styles = createStyles({
    root: {
      height: '100%',
      width: '100%',
      overflow: 'visible',
      display: 'flex',
      'flex-direction': 'column',
      'align-items': 'center',
    },
    containerElement: {
      'min-height': '200px',
      height: '100%',
      width: '100%',
      flex: '1',
    },
    mapElement: {
      height: '100%',
      width: '100%',
    },
    loadingElement: {
      height: '100%',
      width: '100%',
    },
  });

  state = {
    mapMounted: false,
  };

  _mapRef = null;

  _handleOnLoad = map => {
    if (!map || this._mapRef) {
      return;
    }
    this._mapRef = map;

    this.setState({
      mapMounted: true,
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
        // @ts-ignore
        decodedPolyline = window.google.maps.geometry.encoding.decodePath(
          this.props.activity.properties.map.summary_polyline
        );
      }

      // @ts-ignore
      var bounds = new window.google.maps.LatLngBounds();
      decodedPolyline.forEach(point => {
        bounds.extend(point);
      });
      this._mapRef.fitBounds(bounds);

      this.setState({
        decodedPolyline: decodedPolyline,
        bounds: bounds,
      });
    }
  }

  render() {
    return (
      <LoadScript
        id="script-loader"
        googleMapsApiKey={config.mapsApiKey}
        libraries={MAP_LIBRARIES}
        loadingElement={<div className={this.props.classes.loadingElement} />}
      >
        <GoogleMap
          mapContainerClassName={this.props.classes.containerElement}
          onLoad={this._handleOnLoad}
          zoom={10}
        >
          <Polyline
            path={this.state.decodedPolyline}
            visible
            options={{
              strokeColor: '#ff4081',
              strokeOpacity: 1,
              strokeWeight: 3,
            }}
          />
          <BicyclingLayer autoUpdate />
        </GoogleMap>
      </LoadScript>
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
      'align-items': 'center',
    },
    activityRow: {
      width: '100%',
    },
    activitySummary: {
      width: '100%',
      display: 'flex',
      'align-items': 'stretch',
    },
    activitySummaryItem: {
      width: '100%',
    },
  };

  static propTypes = {
    profile: PropTypes.object,
    activity: PropTypes.object,
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

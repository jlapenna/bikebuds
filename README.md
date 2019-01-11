# Bikebuds

This is not an officially supported Google product.

## Overview

A hodge-podge of features to help encourage bikebuds to get out and be active.

## Architecture

### Authentication

Uses firebase for authentication and user management.

### Services

Three major services all running on standard environment Python App Engine:
frontend, backend, api.

#### Frontend

React + Material-UI

Based on the create-react-app npm app, extended with several other react libraries.

   * https://github.com/facebook/create-react-app
   * https://material-ui.com/
   * https://github.com/firebase/firebaseui-web-react
   * https://github.com/firebase/firebaseui-web/
   * etc...


#### Backend

Standard Flask App Engine Service.

#### API

Python Cloud Endpoints Frameworks v2.

### Android

Uses Official Material Components, firebase libraries and play services.

### Flutter

(Replaces Android app)

Uses Official Flutter components and firebase libraries.

## Development

Most details below assume you're using a linux machine for development.

### Dependencies

bikebuds development requires:

* gCloud CLI
  * https://cloud.google.com/sdk/gcloud/
* AppEngine SDK
  * https://cloud.google.com/appengine/downloads (For python)
* NPM
  * https://www.npmjs.com/get-npm
* Flutter SDK
  * https://flutter.io/docs/get-started/install
* Python 2.x
  * https://www.python.org/downloads/ (See "Specific Releases").
* PIP 2.x
  * https://pypi.org/project/pip/
* virtualenv
  * https://virtualenv.pypa.io/en/latest/


### Setup

From the root directory:

```
./setup/dev.sh  # Installs pre-reqs
# Ensure you have the proper service keys in private/service_keys
./setup/env.sh  # Sets up 
```

### Private files

bikebuds/private should exist with the following files, which you'll need to
generate for yourself.

Note: A private git repo for admins only can be found at:
https://source.developers.google.com/p/bikebuds-app/r/private

```
private
├── debug.keystore
├── prod.jks
└── service_keys
    ├── bikebuds-app-firebase-adminsdk-888ix-2dfafbb556.json
    ├── fitbit.json
    ├── fitbit-local.json
    ├── strava.json
    ├── strava-local.json
    ├── withings.json
    └── withings-local.json
```

#### fitbit.json
```
{
  "admin_account": "user@domain",
  "client_id": "XXX",
  "client_secret": "YYY",
  "callback_url": "http://localhost:8082/fitbit/redirect",
  "authorization_uri": "https://www.fitbit.com/oauth2/authorize",
  "access_token_request_uri": "https://api.fitbit.com/oauth2/token"
}
```

#### strava.json
```
{
  "client_id": "XXX",
  "client_secret": "YYY",
  "access_token": "ZZZ"
}
```

#### withings.json
```
{
  "admin_account": "user@domain",
  "client_id": "XXX",
  "client_secret": "YYY",
}
```

### Running Local Backend & Frontend Services

```
./gae/local.sh
```

You should be able to visit localhost:8080 to see the frontend.

Note: localhost:8081 also serves the frontend, but it will serve the latest 
production npm build of the react app. You probably dont' want this.

### API Updates

Whenever you add a new API method or modify its signature, be sure to generate
new API specs:

```
./gae/update_api.sh local
```

### Local flutter development

Set up port-forwards on your android device so the flutter app can talk to the
local backend.

```
./setup/android.sh
```

## Production

If you're not jlapenna@ you can stop reading. ;)

```
./gae/deploy.sh
```

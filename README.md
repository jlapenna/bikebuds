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

## Development

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

### Local backends

```
./gae/local.sh
```

You should be able to visit localhost:8080 to see the frontend.

### API Updates

If you add a new API method (or you're starting android dev), be sure to call
update_api:

```
./gae/update_api.sh local
```

### Local android development

Build a client jar (do this once or when changing the api) and set-up port
forwards (do this every time you plug in your device)..

```
./gae/update_api.sh local
./android/local.sh
# Launch your APK.
```

## Production

If you're not jlapenna@ you can stop reading. ;)

```
./gae/deploy.sh
git checkout .
```

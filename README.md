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

Uses Official Material Components, firebase libraries and play services. Deprecated.

### Flutter

(Replaces Android app)

Uses Official Flutter components and firebase libraries.

## Development

Most details below assume you're using a linux machine for development.

### Dependencies

bikebuds development requires:

* Python 2.7
  * https://www.python.org/downloads/ (See "Specific Releases").
* PIP 2.x
  * https://pypi.org/project/pip/
* virtualenv
  * https://virtualenv.pypa.io/en/latest/
* gCloud CLI
  * https://cloud.google.com/sdk/gcloud/
* NPM
  * https://www.npmjs.com/get-npm
* Android Studio
  * package:args/args.dart
* Flutter SDK
  * https://flutter.io/docs/get-started/install


### Setup

From the root directory:

```
# Ensure you have the right apps on your machine to do development.
./tools/setup/dev.sh  # Installs pre-reqs

# Ensure the source tree links to the proper configs, so you can compile.
./tools/setup/env.sh  # Sets up 
```

After running `tools/setup/dev.sh`, you need to edit a file because of the way our
spec file is generated. You'll want to apply this diff:
```
diff --git a/lib/src/dart_resources.dart b/lib/src/dart_resources.dart
index 9ed04ae..0d180f3 100644
--- a/lib/src/dart_resources.dart
+++ b/lib/src/dart_resources.dart
@@ -218,20 +218,15 @@ class DartResourceMethod {
     validatePathParam(MethodParameter param) {
       templateVars[param.jsonName] = param.name;
 
-      if (param.required) {
-        if (param.type is UnnamedArrayType) {
-          params.writeln(
-              '    if (${param.name} == null || ${param.name}.isEmpty) {');
-        } else {
-          params.writeln('    if (${param.name} == null) {');
-        }
-        params.writeln('      throw new ${imports.core.ref()}ArgumentError'
-            '("Parameter ${param.name} is required.");');
-        params.writeln('    }');
+      if (param.type is UnnamedArrayType) {
+        params.writeln(
+            '    if (${param.name} == null || ${param.name}.isEmpty) {');
       } else {
-        // Is this an error?
-        throw 'non-required path parameter';
+        params.writeln('    if (${param.name} == null) {');
       }
+      params.writeln('      throw new ${imports.core.ref()}ArgumentError'
+          '("Parameter ${param.name} is required.");');
+      params.writeln('    }');
     }
 
     encodeQueryParam(MethodParameter param) {
```

### Evironment Configs

The setup script directs you to clone some environment git repos. There are two,
dev and prod.

If you're jlapenna, you need prod to push; otherwise you only need dev. If
you're on the dev geam, you can clone that with the provided command.

If you're jlapenna or the dev team, you can create a directory that looks a lot
like this:

```
dev
├── app_configs
│   ├── GoogleService-Info-app.plist
│   ├── GoogleService-Info-next.plist
│   ├── google-services-app-android.json
│   └── google-services-next-android.json
├── config.json
├── debug.keystore
├── dev -> dev
└── service_keys
    ├── firebase-adminsdk.json
    ├── fitbit.json
    ├── strava.json
    └── withings.json
```

#### dev/config.json
```
{
  "project_id": "",

  "api_key": "",
  "auth_domain": "",
  "database_url": "",
  "storage_bucket": "",
  "message_sender_id": "",
  "vapid_key": "",


  "next_project_id": "",
  "next_api_key": "",
  "next_auth_domain": "",
  "next_database_url": "",
  "next_storage_bucket": "",
  "next_message_sender_id": "",

  "devserver_url": "http://localhost:8080",
  "frontend_url": "http://localhost:8081",
  "api_url": "http://localhost:8082",
  "backend_url": "http://localhost:8083"
}
```

#### dev/service_keys/fitbit.json
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

#### dev/service_keys/strava.json
```
{
  "client_id": "XXX",
  "client_secret": "YYY",
  "access_token": "ZZZ"
}
```

#### dev/service_keys/withings.json
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
./flutter/local.sh
```

## Production

If you're not jlapenna@ you can stop reading. ;)

### Backend

```
./gae/deploy.sh
```

### Flutter

```
./flutter/release.sh
```

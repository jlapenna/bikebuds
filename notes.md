# Cloud Console

Money:
* https://cloud.google.com/appengine/docs/standard/python/console/#setting_a_spending_limit
* https://console.cloud.google.com/appengine/settings?project=bikebuds-app
* https://cloud.google.com/appengine/pricing#spending_limit
* https://console.cloud.google.com/billing/0011D9-CEF324-FFD4AA/budgets?organizationId=0
Code:
        https://source.cloud.google.com/bikebuds-app/bikebuds/+/master:
* https://source.cloud.google.com/bikebuds-app/bikebuds/+/master
* git clone https://source.developers.google.com/p/bikebuds-app/r/bikebuds

Emulator:
* /home/jlapenna/android/sdk/emulator/emulator -netdelay none -netspeed full -avd Pixel_2_API_28

Credentials:
* https://console.developers.google.com/apis/credentials?project=bikebuds-app

Code Style:
* Import into Android Studio, android/codestyles/AndroidStyle.xml
* Manage Code Styles -> set from (RHS of dialog, select android)

Cloud Repositories
* curl https://sdk.cloud.google.com | bash
* exec -l $SHELL
* gcloud init

"""
Before I asked why GAE can't find TensorFlow lib here https://stackoverflow.com/questions/40241846/why-googleappengine-gives-me-importerror-no-module-named-tensorflow

And Dmytro Sadovnychyi told me that GAE can't run TensorFlow, but GAE flexible can.
"""

https://cloud.google.com/appengine/docs/flexible/python/flexible-for-standard-users
The flexible environment is intended to be complementary to the standard
environment. If you have an existing application running in the standard
environment, it’s not usually necessary to migrate the entire application to
the flexible environment. Instead, identify the parts of your application that
require more CPU, more RAM, a specialized third-party library or program, or
that need to perform actions that aren’t possible in the standard environment.
Once you’ve identified these parts of your application, create small App Engine
services that use the flexible environment to handle just those parts. Your
existing service running in the standard environment can call the other
services using HTTP, Cloud Tasks alpha, or Cloud Pub/Sub.  """


https://github.com/armujahid/appengine-tensorflow-python3
https://cloud.google.com/appengine/docs/standard/go/quickstart


Choosing an environment
https://cloud.google.com/appengine/docs/the-appengine-environments
https://cloud.google.com/solutions/mobile/mobile-app-backend-services

# commands I've run
```sh
gcloud --project=bikebuds-app app domain-mappings list
gcloud --project=bikebuds-app app domain-mappings create bikebuds.joelapenna.com
gcloud --project=bikebuds-app domains list-user-verified
gcloud --project=bikebuds-app app logs tail -s frontend
gcloud --project=bikebuds-app app logs tail -s backend
```

# Things that have helped
* https://github.com/hozn/stravalib
* https://github.com/hozn/stravalib/issues/58 - Developing with GAE

# Use Cloud Endpoints to serve an API and do stuff.
* https://console.cloud.google.com/endpoints?project=bikebuds-app
* https://cloud.google.com/endpoints/docs/frameworks/python/get-started-frameworks-python
* https://cloud.google.com/endpoints/docs/frameworks/python/about-cloud-endpoints-frameworks
* https://cloud.google.com/endpoints/docs/frameworks/python/get-started-frameworks-python
* https://cloud.google.com/endpoints/docs/frameworks/python/authenticating-users#authenticating_with_firebase_auth
* https://medium.com/@anttihavanko/firebase-authentication-with-google-cloud-endpoints-e0a2a8d5c537
* https://cloud.google.com/blog/products/gcp/google-cloud-endpoints-now-ga-a-fast-scalable-api-gateway
* https://cloud.google.com/endpoints/docs/frameworks/python/gen_clients
* https://developers.google.com/apis-explorer/?base=http://localhost:8081/_ah/api#p/

* https://cloud.google.com/endpoints/docs/frameworks/java/calling-from-android
  *  https://developers.google.com/api-client-library/java/google-http-java-client/android
  *  https://developers.google.com/api-client-library/java/google-http-java-client/json
  *  https://cloud.google.com/endpoints/docs/frameworks/java/migrating-android

* https://cloud.google.com/endpoints/docs/frameworks/java/calling-from-javascript
  * https://github.com/google/google-api-javascript-client/issues/399

* https://github.com/GoogleCloudPlatform/java-docs-samples/issues/923
* ENDPOINTS_SERVICE_VERSION is optional

Portal:
* https://console.cloud.google.com/endpoints/portal?project=bikebuds-app
* https://endpointsportal.bikebuds-app.cloud.goog/settings
* https://docs.bikebuds.joelapenna.com/settings

# android api
requires installing gradle. apt install gradle.

# examples
curl 'http://localhost:8080/_ah/api/discovery/v1/apis/bikebuds/v1/rest'
google-chrome --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8081 'http://localhost:8081/_ah/api/explorer'

# Cookies & Sessions
https://firebase.google.com/docs/admin/setup
https://firebase.google.com/docs/auth/admin/manage-cookies
https://medium.com/@hiranya911/firebase-introducing-session-cookies-for-server-side-web-apps-fb46cce40b2

# Auth
* https://developers.google.com/identity/one-tap/web/get-started
  * make sure to add domains in oauth console...
* https://firebase.google.com/docs/auth/
* https://sookocheff.com/post/appengine/cloud-endpoints/using-basic-authentication-with-google-cloud-endpoints/

# requires google-auth

```
(Pdb) auth_header=self.request_state.headers.get('authorization')
(Pdb) auth_token=auth_header[1]
*** TypeError: 'NoneType' object is not callable
(Pdb) import google.auth.transport.requests
(Pdb) import requests_toolbelt.adapters.appengine
(Pdb) HTTP_REQUEST = google.auth.transport.requests.Request()
(Pdb) 
(Pdb) id_token=auth_token
(Pdb) google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
*** TransportError: ('Connection aborted.', error(13, 'Permission denied'))
(Pdb) 
```

# Prod deploy problems:
Failed to load https://backend.bikebuds.cc/create_session: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource. Origin 'https://bikebuds.joelapenna.com' is therefore not allowed access.
but then:
https://stackoverflow.com/questions/50289065/google-yolo-stop-working-the-client-origin-is-not-permitted-to-use-this-api
looks like its got an abuse problem and temporarily disabled.

# Copyrights
for i in $fileswithoutheaders; do echo $i; cat apache_header.py > $i.copy; cat $i >> $i.copy; mv $i.copy $i; done;

# dev setup problems:
If you encounter the error message DistutilsOptionError: can't combine user with prefix, exec_prefix/home, or install_(plat)base, then you will need to create a virtual environment.

# API Problems
Adding a GET endpoint with a request that has a message body (not VoidMessage):
    File "/home/jlapenna/code/bikebuds/gae/backend/lib/endpoints/openapi_generator.py", line 378, in __body_parameter_descriptor
      self.__request_schema[method_id])
  KeyError: 'bikebuds.get_user'
  spec file not created.
https://github.com/cloudendpoints/endpoints-python/issues/126

# withings

get_measures returns NokiaMeasureGroup.

# React

* https://www.robinwieruch.de/minimal-react-webpack-babel-setup/
* https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi/related

# SSL CERTIFICATE 

To create a cert and validate we own its domain:

```shell
./certbot-auto --manual certonly -d '*.bikebuds.cc';
rm -rf bikebuds.cc-cert/;
sudo cp -Lr /etc/letsencrypt/live/bikebuds.cc bikebuds.cc-cert;
sudo chown -R jlapenna bikebuds.cc-cert;
openssl rsa \
    -in bikebuds.cc-cert/privkey.pem \
    -out bikebuds.cc-cert/privkey_rsa.pem;
```

To update the cert on gcp:

```shell
gcloud app ssl-certificates update 12362252 \
    --display-name star-dot-bikebuds.cc \
    --certificate bikebuds.cc-cert/fullchain.pem \
    --private-key bikebuds.cc-cert/privkey_rsa.pem;
```

To create a new cert and associated mapping:

```shell
#gcloud app ssl-certificates create \
#    --display-name star-dot-bikebuds.cc \
#    --certificate bikebuds.cc-cert/fullchain.pem \
#    --private-key bikebuds.cc-cert/privkey_rsa.pem;
#gcloud app domain-mappings update '*.bikebuds.cc' \
#    --certificate-id 12362252;
```

## Proper configuration:
```
$ gcloud app ssl-certificates list
ID        DISPLAY_NAME          DOMAIN_NAMES
10654169  managed_certificate   apidocs.bikebuds.cc
11115986  star-dot-bikebuds.cc  *.bikebuds.cc

$ gcloud app domain-mappings list
ID             SSL_CERTIFICATE_ID  SSL_MANAGEMENT_TYPE  PENDING_AUTO_CERT
*.bikebuds.cc  11115986            MANUAL
bikebuds.cc                        AUTOMATIC            11114599
```

# Keys and Clients

* "Server key (auto created by Google Service)" -> https://console.firebase.google.com/u/0/project/bikebuds-app/settings/cloudmessaging/android:cc.bikebuds
* "Web General Key" -> https://console.firebase.google.com/u/0/project/bikebuds-app/settings/general/android:cc.bikebuds
* "Web client (auto created by Google Service)" -> https://console.firebase.google.com/u/0/project/bikebuds-app/authentication/providers -> GoogleProvider Web SDK
* "Android Client (App Signing Key)" -> https://console.firebase.google.com/u/0/project/bikebuds-app/authentication/providers -> GoogleProviderWhitelist
* "Android Client (Upload Key)" -> https://console.firebase.google.com/u/0/project/bikebuds-app/authentication/providers -> GoogleProviderWhitelist

Due to cross-auth, make sure that your firebase "-next" project's Google auth provider whitelists the "Web Client (auto created by Google Service)" oauth2 client id.

# Stackdriver

* https://cloud.google.com/trace/docs/reference/v1/rest/v1/projects.traces
* https://cloud.google.com/trace/docs/reference/v1/rest/v1/projects/patchTraces?apix_params=%7B%22projectId%22%3A%22bikebuds-app%22%2C%22prettyPrint%22%3Atrue%2C%22resource%22%3A%7B%22traces%22%3A%5B%7B%22spans%22%3A%5B%7B%22name%22%3A%22NAME%22%2C%22startTime%22%3A%222019-01-03T00%3A03%3A39.008000Z%22%2C%22endTime%22%3A%222019-01-03T00%3A03%3A40.008000Z%22%2C%22kind%22%3A%22SPAN_KIND_UNSPECIFIED%22%2C%22spanId%22%3A555555%7D%5D%2C%22projectId%22%3A%22bikebuds-app%22%2C%22traceId%22%3A%220254be7320a2d41e9d1667ed55491413%22%7D%5D%7D%7D
https://cloud.google.com/trace/docs/reference/


# Dart and libraries

```
PATH=$PATH:/home/jlapenna/android/sdk/platform-tools:/home/jlapenna/flutter/sdk/bin
PATH="$PATH":"$HOME/.pub-cache/bin":"$HOME/flutter/sdk/bin/cache/dart-sdk/bin"

cd flutter/sdk
git clone https://github.com/dart-lang/discoveryapis_generator.git

cd discoveryapis_generator
```

```
edit lib/src/dart_resources.dart, removing if condition only keeping if contents near """
      } else {
        // Is this an error?
        throw 'non-required path parameter';
      }
```

```
cp ../../code/bikebuds/gae/api/bikebuds-v1.discovery ~/disc/bikebuds.json
dart bin/generate.dart package  -i ../../disc/ -o ../../code/bikebuds/generated/bikebuds_api --package-name=bikebuds_api
```


# FCM python notes

* https://firebase.google.com/docs/cloud-messaging/admin/errors
  * exception.code is dashed string version of above.

```
        message = messaging.Message(
            data={},
            token=client_store.client.id + "adfasdfa",
        )

        try:
            response = messaging.send(message)
	    message_id = response[1] # eg 'projects/bikebuds-app/messages/0:1546730789539629%e4196d51f9fd7ecd'
            logging.debug('Successfully sent message:', response)
        except messaging.ApiCallError, e:
            logging.info('Error: %s', e);
```

# Safari didn't load.

It was third party cookies. so I set up a firebase custom domain:

* https://firebase.google.com/docs/hosting/custom-domain
* https://stackoverflow.com/questions/51262419/ssl-certificate-generated-by-firebase-hosting-does-not-include-connected-domain
* https://console.firebase.google.com/project/bikebuds-app/hosting/main
* https://console.developers.google.com/apis/credentials/oauthclient/294988021695-ig6caq2he7mg493s423mhi26r12r3c77.apps.googleusercontent.com?project=bikebuds-app

# Querying the API on localhost.

1. Assuming you have the api up and running via `gae/local.sh`
2. Open http://localhost:8080, make sure you're signed in and open the network inspector.
3. Reload the page
3. Find the POST request `token?key=...`_and `copy as cuRL.`
4. Execute the curl command to get an auth token:

       AUTH_TOKEN=$(curl 'https://securetoken.googleapis.com/v1/token?key=AIzaSyCpP9LrZJLnK2UlOYKjRHXijZQHzwGjpPU' -H 'Referer: http://localhost:8080/' -H 'Origin: http://localhost:8080' -H 'X-Client-Version: Chrome/JsCore/5.5.9/FirebaseCore-web' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 ^Cfari/537.36' -H 'Content-Type: application/x-www-form-urlencoded' --data 'grant_type=refresh_token&refresh_token=thiswillbeaverylongstringthatyoullgetanduseits' --compressed|python -c 'import sys; import json; print json.load(sys.stdin)["access_token"];')

5. Execute your API request:

       curl 'http://localhost:8082/_ah/api/bikebuds/v1/series?key=AIzaSyCpP9LrZJLnK2UlOYKjRHXijZQHzwGjpPU' -X POST -H "Authorization: Bearer $AUTH_TOKEN"

# Strava web push.

# Subscribing

curl -G https://api.strava.com/api/v3/push_subscriptions     -d client_id=XXX     -d client_secret=YYY

curl -X POST https://api.strava.com/api/v3/push_subscriptions \
      -F client_id=XXX \
      -F client_secret=YYY \
      -F 'callback_url=https://bikebuds.cc/services/strava/events' \
      -F 'verify_token=ZZZ'

responds with:
{"id":333333,"resource_state":2,"application_id":77777,"callback_url":"https://bikebuds.cc/services/strava/events","created_at":"2019-02-02T17:55:59.510256816Z","updated_at":"2019-02-02T17:55:59.510255963Z"}

## pushing a test event

curl -H 'Content-Type: application/json' -X POST 'http://localhost:8081/services/strava/events' -d '{
     "aspect_type": "create",
     "event_time": 1549151211,
     "object_id": 2120517859,
     "object_type": "activity",
     "owner_id": 35056021,
     "subscription_id": 133263,
     "updates": {}
     }'

# Withings web push.

# Subscribing

One subscription per user, subscribed on every user sync. nokia_client.subscribe()

## Pushing a test event

curl -H 'Content-Type: application/x-www-form-urlencoded' -X POST 'http://localhost:8081/services/withings/events?sub_secret=XXXXXXXXXXXX&service_key=URLSAFE_SERVICE_KEY' -d 'userid=17012450&startdate=1532017199&enddate=1532017200&appli=1'

# Play Store Automatic publication

## Service account for release management

https://developers.google.com/android-publisher/getting_started#using_a_service_account

1.  Create a role account: https://play.google.com/apps/publish/?account=5211640537439974576#ApiAccessPlace
2.  Add the user to play store console: https://play.google.com/apps/publish/?account=5211640537439974576#AdminPlace
    1.  Should be a "Release Manager."
    2.  Be sure to include the app you intend to manage.

# Cloud Tasks

Not supported locally.

```
gcloud --project=bikebuds-app tasks queues create default
```

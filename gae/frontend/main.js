// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

$(function() {
  var apiHostUrl = 'http://localhost:8081';
  var backendHostUrl = 'http://localhost:8082';
  // Local development fails due to CORS...
  //var bikebudsDiscoveryUrl = backendHostUrl + '/_ah/api/discovery/v1/apis/bikebuds/v1/rest'
  // Should be the same as the app server one...
  var bikebudsDiscoveryUrl = apiHostUrl + '/bikebuds-v1.discovery';

  var config = {
    apiKey: "AIzaSyCpP9LrZJLnK2UlOYKjRHXijZQHzwGjpPU",
    authDomain: "bikebuds-app.firebaseapp.com",
    databaseURL: "https://bikebuds-app.firebaseio.com",
    projectId: "bikebuds-app",
    storageBucket: "bikebuds-app.appspot.com",
    messagingSenderId: "294988021695",
  };

  // Firebase log-in widget
  function configureFirebaseLoginWidget() {
    var uiConfig = {
      callbacks: {
        signInSuccessWithAuthResult: function(authResult, redirectUrl) {
          // Return false to not redirect
          return false;
        },
        signInFailure: function(error) {
          // Some unrecoverable error occurred during sign-in.
          // Return a promise when error handling is completed and FirebaseUI
          // will reset, clearing any UI. This commonly occurs for error code
          // 'firebaseui/anonymous-upgrade-merge-conflict' when merge conflict
          // occurs. Check below for more details on this.
          return handleUIError(error);
        },
        uiShown: function() {
          // The widget is rendered.
        }
      },
      signInSuccessUrl: '/',
      signInOptions: [
        {
          provider: firebase.auth.GoogleAuthProvider.PROVIDER_ID,
          // Required to enable one-tap sign-up for YOLO
          //authMethod: 'https://accounts.google.com',
        },
      ],
      // Required to enable one-tap sign-up for YOLO
      //credentialHelper: firebaseui.auth.CredentialHelper.GOOGLE_YOLO
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
  }

  // Listens for state changes related to login.
  function listenToAuthStateChanges() {
    firebase.auth().onAuthStateChanged(function(user) {
      if (user) {
        var name = user.displayName;
        var welcomeName = name ? name : user.email;
        $('#user').text(welcomeName);
        $('#logged-in').show();
        $('#logged-out').hide();

        // Establish a cookie based session for this user for when we hit the
        // backend.
        user.getIdToken().then(createSession);

        // Then load the gapi client and set up its authentication.
        loadGapi();
      } else {
        $('#logged-in').hide();
        $('#logged-out').show();

      }
    });
  }

  function createSession(idToken) {
    console.log('createSession');
    return $.ajax(backendHostUrl + '/create_session', {
      /* Set header for the XMLHttpRequest to get data from the web server
      associated with userIdToken */
      headers: {
        'Authorization': 'Bearer ' + idToken
      },
      method: 'POST',
      xhrFields: {
        withCredentials: true
      },
    }).then(function(data){
      console.log("createSession: complete", data);
    });
  }

  function closeSession(idToken) {
    console.log('closeSession');
    return $.ajax(backendHostUrl + '/close_session', {
      /* Set header for the XMLHttpRequest to get data from the web server
      associated with userIdToken */
      headers: {
        'Authorization': 'Bearer ' + idToken
      },
      method: 'POST',
      xhrFields: {
        withCredentials: true
      },
    }).then(function(data){
      console.log("closeSession: complete: " + data);
    });
  }

  function stravaInit(idToken) {
    console.log('stravaInit');
    $.ajax(backendHostUrl + '/strava_init', {
      /* Set header for the XMLHttpRequest to get data from the web server
      associated with userIdToken */
      headers: {
        'Authorization': 'Bearer ' + idToken
      },
      method: 'POST',
      xhrFields: {
        withCredentials: true
      },
    }).then(function(data){
      console.log("stravaInit complete");
    });
  }

  function callTestAjax(idToken) {
    console.log('callTestAjax');
    return $.ajax(backendHostUrl + '/test_ajax', {
      /* Set header for the XMLHttpRequest to get data from the web server
      associated with userIdToken */
      headers: {
        'Authorization': 'Bearer ' + idToken
      }
    }).then(function(data){
      console.log("callTestAjax: complete: " + data);
    });
  }

  function signOutUser() {
    var user = firebase.auth().currentUser;
    user.getIdToken().then(function(idToken) {
      closeSession(idToken);
      firebase.auth().signOut().then(function() {
        console.log("Sign out successful");
      }, function(error) {
        console.log(error);
      });
    });
  }

  function listenToSignOutButton() {
    // Sign out a user
    var signOutBtn = $('#sign-out');
    signOutBtn.click(function(event) {
      event.preventDefault();
      signOutUser();
    });
  }

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

  /** Loads the gapi libraries and queues client loading. */
  function loadGapi(idToken) {
    // Load the API client library.
    var loadGapiPromise = new Promise(function(resolve, reject) {
      gapi.load('client', resolve);
    });

    // Fetch the Bikebuds API discovery served on local server. You can also
    // pack the json as a string to avoid extra network request.
    // After this promise is fulfilled, the bikebudsDiscovery variable
    // will be set.
    var bikebudsDiscoveryPromise = fetch(bikebudsDiscoveryUrl).then(
      function(resp){
        // resp.json() returns a promise...
        return resp.json();
      });
    // When both the gapi.client is loaded and the discovery JSON object
    // is ready, call initClient to start API call.
    Promise.all([loadGapiPromise, bikebudsDiscoveryPromise]).then(
      function(result) {
        let [unused, bikebudsDiscovery] = result;
        initJsClient(bikebudsDiscovery);
      });
  }

  function main() {
    // Initialize Firebase
    firebase.initializeApp(config);

    configureFirebaseLoginWidget();
    listenToAuthStateChanges();
    listenToSignOutButton();
  }

  main();

});

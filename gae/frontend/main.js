$(function() {
  var backendHostUrl = 'http://localhost:8081';

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
          authMethod: 'https://accounts.google.com',
          clientId: '294988021695-47fbiinqpoa0n4pb7qp9khlsdl0leaf1.apps.googleusercontent.com'
        },
      ],
      // Required to enable one-tap sign-up credential helper.
      // This will auto-signin a user.
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

        user.getIdToken().then(createSession);
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
      console.log("createSession: complete: " + data);
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

  function main() {
    // Initialize Firebase
    var config = {
      apiKey: "AIzaSyCzIzSoOZe6mlkxbSvfvi4zI8AJwlUN94k",
      authDomain: "bikebuds-app.firebaseapp.com",
      databaseURL: "https://bikebuds-app.firebaseio.com",
      projectId: "bikebuds-app",
      storageBucket: "bikebuds-app.appspot.com",
      messagingSenderId: "294988021695"
    };
    firebase.initializeApp(config);

    configureFirebaseLoginWidget();
    listenToAuthStateChanges();
    listenToSignOutButton();
  }

  main();

});

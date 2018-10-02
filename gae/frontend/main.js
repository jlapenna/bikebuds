$(function() {
  var backendHostUrl = 'http://localhost:8081';

  // Initialize Firebase
  var config = {
    apiKey: "AIzaSyCzIzSoOZe6mlkxbSvfvi4zI8AJwlUN94k",
    authDomain: "bikebuds-app.firebaseapp.com",
    databaseURL: "https://bikebuds-app.firebaseio.com",
    projectId: "bikebuds-app",
    storageBucket: "bikebuds-app.appspot.com",
    messagingSenderId: "294988021695"
  };

  // Firebase log-in
  function configureFirebaseLogin() {

    firebase.initializeApp(config);

    firebase.auth().onAuthStateChanged(function(user) {
      if (user) {
        $('#logged-out').hide();
        var name = user.displayName;

        /* Use the user's name or email for a custom message. */
        var welcomeName = name ? name : user.email;

        user.getIdToken().then(function(idToken) {
          /* Now that the user is authenicated, Do things... */
          $('#user').text(welcomeName);
          $('#logged-in').show();
          createSession(idToken);
        });

      } else {
        $('#logged-in').hide();
        $('#logged-out').show();

      }
      // [END gae_python_state_change]

    });

  }

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
      credentialHelper: firebaseui.auth.CredentialHelper.GOOGLE_YOLO
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
  }

  function createSession(idToken) {
    console.log('createSession');
    $.ajax(backendHostUrl + '/create_session', {
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
      console.log("createSession complete");
    });
  }

  function closeSession(idToken) {
    console.log('closeSession');
    $.ajax(backendHostUrl + '/close_session', {
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
      console.log("closeSession: complete");
    });
  }

  function callTestAjax(idToken) {
    $.ajax(backendHostUrl + '/test_ajax', {
      /* Set header for the XMLHttpRequest to get data from the web server
      associated with userIdToken */
      headers: {
        'Authorization': 'Bearer ' + idToken
      }
    }).then(function(data){
      console.log("Fetched: " + data);
    });
  }

  // Sign out a user
  var signOutBtn = $('#sign-out');
  signOutBtn.click(function(event) {
    event.preventDefault();
    var user = firebase.auth().currentUser;
    user.getIdToken().then(function(idToken) {
      closeSession(idToken);
      firebase.auth().signOut().then(function() {
        console.log("Sign out successful");
      }, function(error) {
        console.log(error);
      });
    });
  });

  configureFirebaseLogin();
  configureFirebaseLoginWidget();

});

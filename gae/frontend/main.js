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

        user.getToken().then(function(idToken) {
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
      'signInSuccessUrl': '/',
      'signInOptions': [
        firebase.auth.GoogleAuthProvider.PROVIDER_ID
      ],
      // Terms of service url
      'tosUrl': '<your-tos-url>',
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
    user.getToken().then(function(idToken) {
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

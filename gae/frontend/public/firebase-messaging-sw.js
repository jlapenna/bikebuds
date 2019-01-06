importScripts("https://www.gstatic.com/firebasejs/4.12.0/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/4.12.0/firebase-messaging.js");
let config = {
  messagingSenderId: "294988021695",
};
firebase.initializeApp(config);
const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(payload => {
  console.log('Fcm message received: ', payload);
  if (payload.notification) {
      return self.registration.showNotification(
        'bg handler: ' + payload.notification.title,
        {
          body: 'bg handler: ' + payload.notification.body,
          icon: payload.notification.icon
        }
      );
  } else {
    // Web Push APIs don't support silent notifications, so provide one,
    // otherwise a boring default will be shown.
    return self.registration.showNotification(
      'Bikebuds has updated.',
      {
        body: 'Pardon our interruption.',
        icon: '/favicon.ico',
      }
    );
  }
})

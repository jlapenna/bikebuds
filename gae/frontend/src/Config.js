export const backendConfig = {
  apiHostUrl: (process.env.NODE_ENV === 'development')
      ? 'http://localhost:8081' : 'https://api.bikebuds.cc',
  backendHostUrl: (process.env.NODE_ENV === 'development')
      ? 'http://localhost:8082' : 'https://backend.bikebuds.cc',
}

export const config = {
    apiKey: "AIzaSyCpP9LrZJLnK2UlOYKjRHXijZQHzwGjpPU",
    authDomain: "bikebuds-app.firebaseapp.com",
    databaseURL: "https://bikebuds-app.firebaseio.com",
    projectId: "bikebuds-app",
    storageBucket: "bikebuds-app.appspot.com",
    messagingSenderId: "294988021695",
};

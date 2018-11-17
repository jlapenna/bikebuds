/**
 * Copyright 2018 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export const config = {
    apiKey: "AIzaSyCpP9LrZJLnK2UlOYKjRHXijZQHzwGjpPU",
    authDomain: "bikebuds-app.firebaseapp.com",
    databaseURL: "https://bikebuds-app.firebaseio.com",
    projectId: "bikebuds-app",
    storageBucket: "bikebuds-app.appspot.com",
    messagingSenderId: "294988021695",

    devserverUrl: (process.env.NODE_ENV === 'development')
        ? 'http://localhost:8081' : '',
    frontendUrl: (process.env.NODE_ENV === 'development')
        ? 'http://localhost:8081' : '',
    apiUrl: (process.env.NODE_ENV === 'development')
        ? 'http://localhost:8082' : 'https://api.bikebuds.cc',
    backendUrl: (process.env.NODE_ENV === 'development')
        ? 'http://localhost:8083' : 'https://backend.bikebuds.cc',
};

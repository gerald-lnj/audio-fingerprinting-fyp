# Audio Fingerprinting Frontend

This is the Vue.JS client frontend for the Audio Fingerprinting application.

## Table of Contents

- [Installation](#Installation-and-running)
- [Installation and running with Docker (WIP)](#Installation-and-running-with-Docker-(WIP))
- [Code Structure](#Code-Structure)
- [ENV file (IMPORTANT)](#ENV-file-(IMPORTANT))

## Installation

All commands are to be run in Frontend folder:

```Bash
cd Frontend
```

### Compiles and hot-reloads for development

```Bash
npm run serve
```

### Compiles and minifies for production

```Bash
npm run build
```

### Lints and fixes files

```Bash
npm run lint
```

## Installation and running with Docker (WIP)

The Frontend and Backend of this application can individually work using docker, but I havent got them to work together using docker-compose. Use at your own risk, not tested.

Use the Dockerfile in this folder.

## Code Structure

- src
  - components

    Since there was not much reuse in this frontend, there are no components.

  - router/index.js

      Mapping of routes to views.
  - store/index.js

      Definition of Vuex store that serves as centralised state management. [Read more here](https://vuex.vuejs.org/).

  - utilities/api.js

      Definition of custom function that triggers on JWT token timeout, to automatically get new JWT auth token from server, and use it to retry failed request.

      Used in all API calls to server.
  - views

      Vue single file componets for each view.
  - App.vue

      Main wrapper for overall application. Wraps around each component in src/view.
  - main.js

      Entry point to frontend.

  - uploaded_files

      Folder where uploaded videos are temporarily stored.
  - backend.py

      Entry point to server
- .env_sample
    Sample env file

## ENV file (IMPORTANT)

Duplicate the .env_sample file, and rename it to .env . Do not commit this file, it contains important information such as authentication keys.

- VUE_APP_SERVER_URL = http://localhost:\<flask-server-port-here\>

  Point to dev/production backend server. Defult port should be 5000.

- VUE_JWT_SECRET_KEY = \<your-secret-key\>
  
  Can be literally any string, does not HAVE to be long/complex. Recommended to use ssh-keygen or similar tools. Make sure this key is the same as JWT_SECRET_KEY in backend/.flaskenv .

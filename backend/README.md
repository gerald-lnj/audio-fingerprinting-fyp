# Audio Fingerprinting Backend

This is the Flask server backend for the Audio Fingerprinting application.

## Table of Contents

- [Audio Fingerprinting Backend](#audio-fingerprinting-backend)
  - [Table of Contents](#table-of-contents)
  - [Installation and running](#installation-and-running)
  - [Installation and running with Docker (WIP)](#installation-and-running-with-docker-wip)
  - [Code Structure](#code-structure)
  - [ENV file (IMPORTANT)](#env-file-important)

## Installation and running

All commands are to be run in backend folder:

```Bash
cd backend
```

1. Set up local Python version (OPTIONAL)

   It's recommended to set up a local Python version, so that you can work on mutiple Python projects without worrying about Python versions.

   I recommend [pyenv](https://github.com/pyenv/pyenv).

   If using pyenv, the .python-version file should automatically set Python 3.8.11. If not, use:

   ```Bash
    pyenv local 3.8.11
    ```

2. Install dependencies

    install `poetry`, and dependencies:

    ```python
    pip install poetry
    poetry install
    ```



4. Run backend.py

    backend.py is the entry point to the server.

    ```Bash
    poetry run backend.py
    ```

    This will start a dev server.

## Installation and running with Docker (WIP)

The Frontend and Backend of this application can individually work using docker, but I havent got them to work together using docker-compose. Use at your own risk, not tested.

Use the Dockerfile in this folder.

## Code Structure

- app
  - controllers

    Collection of Python modules related to audio preocessing features.
  - routes

      Collection of Python modules related to handling incoming requrests.
  - schemas

      Collection of Python modules for REST API input validation.

  - init.py

      Setup/config of Flask server.
- output_audio

    Folder where generated ultrasounds are temporarily stored.
- output video

    Folder where videos generated using Audio Watermarking are stored for downloads (deleted after 2 hours)
- source_audio

    Collection of pre-built ultrasound fragments for creating Ultrasound Watermarks. REfer to report for more details.

- uploaded_files

    Folder where uploaded videos are temporarily stored.
- backend.py

    Entry point to server
- .flaskenv_sample
    Sample env file

- Dockerfile

    WIP. Works standalone, but not in conjuctionw ith docker_compose.

## ENV file (IMPORTANT)

Duplicate the .flaskenv_sample file, and rename it to .flaskenv. Do not commit this file, it contains important information such as authentication keys.

- FLASK_APP=backend.py
- MONGO_URI = "mongodb://127.0.0.1:27017/<your-db-name>"

  Assumes you are using the defualt MongoDB local port.
- DEBUG = True
- JWT_SECRET_KEY = <your-key-here>

  Can be literally any string, does not HAVE to be long/complex. Recommended to use ssh-keygen or similar tools. Make sure this key is the same as VUE_JWT_SECRET_KEY in Frontend/.env .
- FLASK_ENV=development
- UPLOADED_VIDEOS_DEST="./uploaded_files"

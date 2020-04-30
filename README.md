# Audio Fingerprinting Application

This application is the Final Year Project of Gerald Lau. It applies Audio Fingerprinting and Audio Watermarking technologies to create an application that embeds and retrieves link into a video.

## Table of Contents

- [Installation Instructions](#Installation-Instructions)
- [Usage Examples](#Usage-Examples)
- [Tips](#Tips)

## Installation Instructions

### Frontend Dependencies

- Node.JS 12.13.0
- NPM 6.12.0
- Vue.JS 2.6.11

### Backend Dependencies

- Python 3.8.0
- Flask 1.1.1
- MongoDB 4.2.5
- FFmpeg 4.2.2

For instruction on how to set up each component, refer to their respective READMEs:

- [Backend README](backend/README.md)
- [Frontend README](Frontend/README.md)

## Usage Examples




## Tips

### Run Mongodb as Service (Mac)

In development/production, it may be desirable to have MongoDB running in the background as a service.

If you have MongoDB installed using Brew, you can use this command:

``` Bash
brew services start mongodb-community@4.2
```

Otherwise, just google around on running MongoDB as a service.

### Run Flask Production Server Using Gunicorn

For this project, Gunicorn was chosen as a production server. A Gunicorn config file is provided in the Backend folder.

To run:

``` Bash
cd backend
gunicorn -c gunicorn.conf.py backend:app
```

You may also want to investigate running the Gunicorn script on startup as a service.

### SSL in Production

As the Frontend requires access to the microphone, browsers will need to run in a secure context, i.e over HTTPS.

In development:

Localhost is excluded from this requirement. To test other domains, you can use a flag in Chrome to get around this:

- [How to access Camera and Microphone in Chrome without HTTPS?](https://stackoverflow.com/questions/52759992/how-to-access-camera-and-microphone-in-chrome-without-https)

In production:

One solution is to create a self-signed SSL certificate to use with the Apache server for the Frontend, and with Gunicorn for the backend.

Read more here:

- [Chrome 47 WebRTC: Media Recording, Secure Origins and Proxy Handling](https://developers.google.com/web/updates/2015/10/chrome-47-webrtc#public_service_announcements)
- [How To Create a Self-Signed SSL Certificate for Apache in Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-apache-in-ubuntu-16-04)
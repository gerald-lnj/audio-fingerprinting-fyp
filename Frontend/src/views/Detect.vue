<template>
  <v-container>
    <div class="videoRec text-xs-center">
      <input 
        ref="video_h" 
        v-model="videoModel"
        type="hidden" 
        name="video" 
      >
      <video
        ref="video"
        class="video"
        controls
      />
      <div class="video-controllers" />
      <v-btn @click="startRecording('video1')">
        Start Recording
      </v-btn>
      <v-btn @click="stopRecording('video1')">
        Pause
      </v-btn>
      <v-btn @click="download('video1')">
        Download
      </v-btn>
    </div>
  </v-container>
</template>

<script>
let RecordRTC = require('recordrtc');
export default {
  name: 'Video',
  data: function () {
    return {
      videoModel:""
    }
  },
  mounted: function () {
    let video = this.$refs.video;
    video.muted = false;
    video.controls = true;
    video.autoplay = false;
  },
  methods: {
    successCallback(stream) {
      var options = {
        mimeType: 'video/webm;codecs=vp9', // or video/webm\;codecs=h264 or video/webm\;codecs=vp9
        audioBitsPerSecond: 128000,
        videoBitsPerSecond: 128000,
        timeSlice:2000,
        bitsPerSecond: 128000 // if this line is provided, skip above two
      };
      this.stream = stream;
      this.recordRTC = RecordRTC(stream, options);
      this.recordRTC.startRecording();
      // let video = this.$refs.video;
      // video.src = window.URL.createObjectURL(stream);
      //this.toggleControls();
    },
    errorCallback() {
      //handle error here
    },
    processVideo(audioVideoWebMURL) {
      let video = this.$refs.video;
      // let recordRTC = this.recordRTC;
      video.src = audioVideoWebMURL;
      //this.toggleControls();
      // var recordedBlob = recordRTC.getBlob();
      // recordRTC.getDataURL(function (dataURL) { });
    },
    startRecording() {
      this.poster="";
      let mediaConstraints = {
      video: {
        mandatory: {
        minWidth: 700,
        minHeight: 720
        }
      }, audio: true
      };
      navigator.mediaDevices
      .getUserMedia(mediaConstraints)
      .then(this.successCallback.bind(this), this.errorCallback.bind(this));
    },
    stopRecording() {
      this.poster="";
      let recordRTC = this.recordRTC;
      recordRTC.stopRecording(this.processVideo.bind(this));
      let stream = this.stream;
      stream.getAudioTracks().forEach(track => track.stop());
      stream.getVideoTracks().forEach(track => track.stop());
    },
    download() {
      this.recordRTC.save('video.webm');
    }
  }
}
</script>

<style scoped>
.title {
  font-family: "Autumn", "Avenir", Helvetica, Arial, sans-serif;
  letter-spacing: 5px;
  font-size: 44px;
  color: white;
}
.login {
  margin-top: 40px;
}
.input {
  width: 75%;
  padding-bottom: 10px;
  padding-top: 10px;
}
button {
  cursor: pointer;
}
p a {
  text-decoration: underline;
  color: #fffb11;
  cursor: pointer;
}
.alert-style {
  min-width: 200px;
}
/* Inserting this collapsed row between two flex items will make
* the flex item that comes after it break to a new row */
.break {
  flex-basis: 100%;
  height: 0;
}

</style>
<template>
  <v-container>
    <v-row>
      <v-col align="center">
        <v-col>
          <audio
            v-if="debug"
            ref="audio"
            controls
            playsinline
          />
        </v-col>
        <v-col>
          <transition name="mic">
            <v-btn
              :class="{'mic': recording}"
              x-large
              color="primary"
              fab
              text 
              icon
              @click="toggleRecording"
            >
              <v-icon>{{ recordingIcon }}</v-icon>
            </v-btn>
          </transition>
        </v-col>

        <v-col>
          <v-btn @click="download">
            Download (DEBUG)
          </v-btn>
        </v-col>
      </v-col>
    </v-row>
  </v-container>
</template>



<script>
import RecordRTC from 'recordrtc'
import Axios from 'axios';
export default {
  name: 'Detect',
  data: function () {
    return {
      recording: false,
      recordingIcon: "mdi-microphone",
      debug: true
    }
  },
  methods: {
    recordRTCOptns() {
      const options = {
        type: 'audio',
        mimeType: 'audio/wav',
        recorderType: RecordRTC.StereoAudioRecorder,
        numberOfAudioChannels: 1,
        desiredSampRate: 44100,
        timeSlice: 5000,
        ondataavailable: (blob) => {
          this.postBlob(blob)
        }
       };
      const isEdge = navigator.userAgent.indexOf('Edge') !== -1 && (!!navigator.msSaveOrOpenBlob || !!navigator.msSaveBlob);
      const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
      console.log(`isEdge: ${isEdge}`)
      console.log(`isSafari: ${isSafari}`)
      if (isSafari||isEdge) {
        options.bufferSize = 4096;
        options.numberOfAudioChannels = 2;
      }

      return options
    },
    postBlob(blob) {
      const server_url = process.env.VUE_APP_SERVER_URL
      const bodyFormData = new FormData();
      bodyFormData.append('audio', blob)
      Axios
      .post(`${server_url}/detect`, bodyFormData)
      .then((msg)=>{
        console.log(msg)
      })
      .catch((error) => {
        console.error(error)
      })
    },
    toggleRecording() {
      if (this.recording) {
        this.recording = false
        this.recordingIcon = "mdi-microphone"
        this.stopRecording()
      } else {
        this.recording = true
        // this.recordingIcon = "mdi-stop"
        this.startRecording()
      }
    },
    successCallback(stream) {
      const options = this.recordRTCOptns()
      this.stream = stream;
      this.recordRTC = RecordRTC(stream, options);
      this.recordRTC.startRecording();
    },
    errorCallback() {
      //handle error here
    },
    processAudio(audioURL) {
      const audio = this.$refs.audio;
      audio.src = audioURL;
    },
    startRecording() {
      const mediaConstraints = { audio: true };
      navigator.mediaDevices
      .getUserMedia(mediaConstraints)
      .then(this.successCallback.bind(this), this.errorCallback.bind(this));
    },
    stopRecording() {
      const recordRTC = this.recordRTC;
      recordRTC.stopRecording(this.processAudio.bind(this));
      const stream = this.stream;
      stream.getAudioTracks().forEach(track => track.stop());
    },
    download() {
      this.recordRTC.save('audio.wav');
      this.recordRTC.ge
    }
  }
}
</script>

<style scoped>
@keyframes shadow-pulse
{
  0% {
    box-shadow: 0 0 0 0px rgba(0, 0, 0, 0.2);
  }
  100% {
    box-shadow: 0 0 0 20px rgba(0, 0, 0, 0);
  }
}

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
.mic
{
  animation: shadow-pulse 1s infinite;
}

</style>
<template>
  <v-container>
    <v-row>
      <v-col align="center">
        <v-col>
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
        </v-col>
        <p v-if="recording">
          {{ detected }}
        </p>
        <v-col>
          <v-card
            :v-if="detectedHistory.length > 0"
            class="d-inline-block mx-auto"
          >
            <transition name="card">
              <virtual-list 
                :size="virtualListSize" 
                :remain="5"
              >
                <v-list-item
                  v-for="entry in detectedHistory"
                  :key="entry.time"
                  :href="entry.data"
                >
                  <v-list-item-content>
                    <v-list-item-title
                      v-text="entry.data"
                    />
                    <v-list-item-subtitle
                      v-text="entry.time"
                    />
                  </v-list-item-content>
                </v-list-item>
              </virtual-list>
            </transition>
          </v-card>
        </v-col>
      </v-col>
    </v-row>
  </v-container>
</template>



<script>
import RecordRTC from 'recordrtc'
import Axios from 'axios';
import moment from 'moment'
import virtualList from 'vue-virtual-scroll-list'
export default {
  name: 'Detect',
  components: {'virtual-list': virtualList},
  data: function () {
    return {
      recording: false,
      recordingIcon: "mdi-microphone",
      debug: true,
      detected: "Waiting...",
      detectedHistory: [],
      updated: false
    }
  },
  computed: {
    virtualListSize() {
      const unit = 12
      const max = 5*unit
      const currentSize = this.detectedHistory.length * unit
      return currentSize < max ? currentSize : max
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
        if (msg.status == 200) {
          const resp = msg.data.message
          console.log(resp)
          this.detected = "Detected!"
          const entry = {
            time: moment().format('h:mm:ss a'),
            data: resp
          }
          this.detectedHistory.push(entry)
          this.updated=true
        }

        else if (msg.status == 204) {
          this.detected = "Waiting..."
        }
      })
      .catch((error) => {
        console.error(error)
        return null
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

    startRecording() {
      const mediaConstraints = { audio: true };
      navigator.mediaDevices
      .getUserMedia(mediaConstraints)
      .then(this.successCallback.bind(this), this.errorCallback.bind(this));
    },
    stopRecording() {
      const recordRTC = this.recordRTC;
      recordRTC.stopRecording();
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
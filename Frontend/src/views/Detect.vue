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
            :disabled="!mode"
            @click="toggleRecording();noDataText='Waiting for results...'"
          >
            <v-icon> mdi-microphone </v-icon>
          </v-btn>
        </v-col>
        <div class="flex-center">
          <v-radio-group
            v-model="mode"
            row
            :mandatory="false"
          >
            <v-radio
              label="Watermarking"
              value="ultrasound"
            />
            <v-radio
              label="Fingerprinting"
              value="audible"
            />
          </v-radio-group>
        </div>
        <v-col>
          <v-data-table
            :headers="headers"
            :items="detectedHistory"
            :sort-desc="true"
            hide-default-header
            hide-default-footer
            :no-data-text=" noDataText"
            class="elevation-1"
            @click:row="openLink"
          >
            <template
              v-slot:top
            >
              <v-toolbar
                flat
                short
              >
                <v-toolbar-title>Detected Links</v-toolbar-title>
                <v-spacer />

                <v-btn @click="detectedHistory = []">
                  Clear Links
                </v-btn>
              </v-toolbar>
            </template>
          </v-data-table>
        </v-col>
      </v-col>
    </v-row>
  </v-container>
</template>



<script>
import RecordRTC from 'recordrtc'
import Axios from '../utilities/api';
import moment from 'moment'
// import VueElementLoading from 'vue-element-loading'

export default {
  name: 'Detect',
  data: function () {
    return {
      recording: false,
      noDataText: 'Tap the microphone to start detection!',
      debug: true,
      headers: [
        {text: 'Time', align: 'start',value: 'time'},
        {text: 'Link', value: 'data'},
      ],
      detectedHistory: [],
      mode: null,
      latestLink: {
        link: null,
        occurences: 0,
      }
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
        timeSlice: 10000,
        ondataavailable: (blob) => {
          this.postBlob(blob)
          this.stopRecording()
          this.startRecording()
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
      bodyFormData.append('mode', this.mode)
      Axios
      .post(`${server_url}/detect`, bodyFormData)
      .then((msg)=>{
        if (msg.status == 200) {
          const resp = msg.data.message
          this.updateDetectedHistory(resp)
        }
      })
      .catch((error) => {
        console.error(error)
        return null
      })
    },
    updateDetectedHistory(link) {
        console.log(link)
        const time = moment().format('h:mm:ss a')
        if (this.latestLink.link == link) {
          this.latestLink.occurences = this.latestLink.occurences + 1
          if (this.latestLink.occurences > 1) {
            const entry = {
              time: time,
              data: link
            }
            this.detectedHistory.push(entry)
          }
        } else {
          this.latestLink.link = link
          this.latestLink.occurences = 1
        }
    },
    toggleRecording() {
      if (this.recording) {
        this.recording = false
        this.stopRecording()
      } else {
        this.recording = true
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
      if (this.recordRTC == null) {
        const mediaConstraints = { audio: true };
        navigator.mediaDevices
        .getUserMedia(mediaConstraints)
        .then(this.successCallback.bind(this), this.errorCallback.bind(this));
      } else {
        const recordRTC = this.recordRTC;
        recordRTC.startRecording()
      }
      
    },
    stopRecording() {
      const recordRTC = this.recordRTC;
      recordRTC.reset()
    },
    download() {
      this.recordRTC.save('audio.wav');
    },
    openLink(entry) {
      window.open(entry.data, '_blank');
    }
  }
}
</script>

<style scoped>
@keyframes shadow-pulse
{
  0% {
    box-shadow: 0 0 0 0px rgba(0, 0, 0, 0.5);
  }
  100% {
    box-shadow: 0 0 0 40px rgba(0, 0, 0, 0);
  }
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
.flex-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
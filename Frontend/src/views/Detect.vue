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
            :disabled="!mode"
            @click="toggleRecording"
          >
            <v-icon>{{ recordingIcon }}</v-icon>
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
        <p v-if="recording">
          {{ detected }}
        </p>
        <v-col>
          <v-data-table
            :headers="headers"
            :items="detectedHistory"
            :sort-desc="true"
            hide-default-header
            hide-default-footer
            no-data-text="Tap the microphone to start detection!"
            class="elevation-1"
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
            <template v-slot:item.action="{ item }">
              <v-btn
                icon
                class="mr-2"
                :href="item.data"
                target="_blank"
              >
                <v-icon small>
                  mdi-open-in-new
                </v-icon>
              </v-btn>
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
export default {
  name: 'Detect',
  data: function () {
    return {
      recording: false,
      recordingIcon: "mdi-microphone",
      debug: true,
      detected: "Waiting...",
      headers: [
        {text: 'Time', align: 'start',value: 'time'},
        {text: 'Link', value: 'data'},
        {text: 'Actions', value: 'action', sortable: false},
      ],
      detectedHistory: [],
      updated: false,
      mode: null
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
  mounted() {
    const mediaConstraints = { audio: true };
    navigator.mediaDevices
    .getUserMedia(mediaConstraints)
    .then(this.successCallback.bind(this), this.errorCallback.bind(this));
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
          this.recordRTC.reset
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
      this.stream = stream;
    },
    errorCallback() {
      //handle error here
    },

    startRecording() {
      this.recordRTC = RecordRTC(this.stream, this.recordRTCOptns());
      this.recordRTC.startRecording();
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
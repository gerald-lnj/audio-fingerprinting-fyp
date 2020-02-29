<template>
  <v-content>
    <v-row
      align="center"
      justify="center"
    >
      <v-col align="center">
        <v-card
          v-show="videoDuration"
          class="mx-auto"
          tile
        >
          <v-col v-show="videoDuration">
            <video
              ref="video"
              controls
              playsinline
              :width="$store.state.windowWidth -4*12"
              height="auto" 
              @timeupdate="insertSeekTime = Math.floor($event.target.currentTime)"
            />
          </v-col>
          <v-col max-width="300">
            <span class="subheading">Duration (Multiples of 10)</span>
            <v-slider
              v-model="insertDuration"
              class="align-center"
              :max="max"
              :min="0"
              step="10"
              ticks="always"
              thumb-label="always"
              :thumb-size="24"
            />
          </v-col>
          <v-col>
            <v-form v-model="tempValid">
              <v-text-field
                v-model="insertSeekTime"
                label="Start (seconds)"
                :rules="[rules.numRules]"
                disabled
              />
              <v-text-field
                v-model="tempEndTime"
                label="End (Seconds)"
                :rules="[rules.numRules]"
                disabled
              />
              <v-text-field
                v-model="tempLink"
                label="Link"
                :rules="[rules.linkRules]"
              />
            </v-form>
          </v-col>
          <v-col>
            <v-btn
              :disabled="(insertDuration<=0) || !tempValid"
              @click="addLink(insertSeekTime, tempEndTime, tempLink)"
            >
              Add link here
            </v-btn>
          </v-col>
        </v-card>
        
        <v-col>
          <v-file-input
            v-model="files"
            accept="video/mp4"
            placeholder="mp4 only!"
            label="Select video"
            :show-size="1000"
            @change="updateVideoDetails"
          />
        </v-col>
        <v-col>
          <v-form v-model="valid">
            <v-container>
              <v-row 
                v-for="(link, index) in linkFormData"
                :key="index"
              >
                <v-text-field
                  v-model="link.start"
                  label="Start (seconds)"
                  required
                  :rules="[rules.numRules]"
                />
                <v-text-field
                  v-model="link.end"
                  label="End (Seconds)"
                  required
                  :rules="[rules.numRules]"
                />
                <v-text-field
                  v-model="link.link"
                  label="Link"
                  required
                  :rules="[rules.linkRules]"
                />
                <v-btn
                  icon
                  @click="deleteLink(index)"
                >
                  <v-icon>mdi-minus-circle</v-icon>
                </v-btn>
              </v-row>
            </v-container>
          </v-form>
        </v-col>
        <v-col>
          <v-btn
            fab
            small
            bottom
            @click="addLink(null, null, '')"
          >
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </v-col>
        <v-col>        
          <v-btn
            bottom
            :disabled="!submit"
            @click="submitRequest"
          >
            Submit
          </v-btn>
        </v-col>
      </v-col>
    </v-row>
  </v-content>
</template>

<script>
import Axios from '../utilities/api';
export default {
  name: "Upload",
  data: () => ({
    tempValid: false,
    insertSeekTime: 0,
    insertDuration: 10,
    tempLink: '',
    videoDuration: null,
    files: null,
    valid: false,
    linkFormData: [
      {
        start: null,
        end: null, 
        link: '',
      }
    ],
    rules: {
      numRules: v => {
        return /([0-9]+)/g.test(v) ? true: "Please enter a number!"
      },
      linkRules: v => {
        if (/(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_+.~#?&//=]*)/g.test(v)) {
          return true
        } else return "Not a valid URL!"
      }
    },
  }),
  computed: {
    tempEndTime: function () {
      return this.insertSeekTime+this.insertDuration
    },
    max: function() {
      const durationRemaining = this.videoDuration - this.insertSeekTime

      return durationRemaining - durationRemaining%10
    },
    snackbar: function() {
      const snackbar = {
        flag: false,
        snackbarMsg: null,
        timeout: 3000
      }

      let error = false
      let errorMessages = []
      for (let i = 0; i < this.linkFormData.length; i++) {
        let currentLink = this.linkFormData[i]

        // set error flag
        if (currentLink.start && currentLink.end && this.videoDuration){ 

          // check start < end
          if (currentLink.start >= currentLink.end) {
            errorMessages.push('Make sure your start and end times are in order!')
            error = true
          }
          
          if ((currentLink.start - currentLink.end) % 10 != 0) {
            errorMessages.push('Duration has to be in multiples of 10 seconds!')
            error = true
          }

          // check links in sequence
          if (i != 0) {
            let prevLink = this.linkFormData[i-1]
            if (currentLink.start < prevLink.end) {
              errorMessages.push('Make sure your links are sequential!')
              error = true
            }
          }

          // check vid duration
          if (i+1 == this.linkFormData.length) {
            if (currentLink.end > this.videoDuration) {
              errorMessages.push("Make sure you don't exceed the video duration!")
              error = true
            }
          }
        }
      }

      if (error) {
        snackbar.flag = error
        snackbar.snackbarMsg = errorMessages.join('\n')
        snackbar.timeout= 0

      }

      this.$store.commit('updateSnackbar', snackbar)

      return snackbar
    },
    submit: function() {
      return (!this.snackbar.flag && this.valid && this.videoDuration && this.linkFormData.length>0)
    }
  },
  methods: {
    updateVideoDetails(file) {
      const vid = this.$refs.video
      if (file) {
        // create url to use as the src of the video
        const fileURL = URL.createObjectURL(file);
        vid.src = fileURL;
        const that=this
        // wait for duration to change from NaN to the actual duration
        vid.ondurationchange = function() {
          that.videoDuration = Math.round(this.duration);
        };
      } else {
        this.videoDuration = null
        vid.src = null
      }
    },
    addLink(start, end, link) {
      const linkTemplate = {
        start: start,
        end: end, 
        link: link
      }

      if (this.linkFormData.length > 0) {
        const lastEntry = this.linkFormData[this.linkFormData.length - 1]

        if (lastEntry.start == null && lastEntry.end==null && lastEntry.link.length == 0) {
          this.linkFormData.pop()
        }
      }
      this.linkFormData.push(linkTemplate)
    },
    deleteLink(index) {
      this.linkFormData.splice(index, 1)
    },
    submitRequest() {
      const server_url = process.env.VUE_APP_SERVER_URL
      const bodyFormData = new FormData();
      const email = this.$store.state.email
      const jwt = this.$store.state.jwt
      const config = {
        headers: {Authorization: `Bearer ${jwt}`}
      }

      this.linkFormData.forEach((entry) => {
        bodyFormData.append('time', `${entry.start}::${entry.end}::${entry.link}`)
      })

      bodyFormData.append('file', this.files)

      bodyFormData.set('email', email)

      Axios
      .post(`${server_url}/upload`, bodyFormData, config)
      .then((resp) => {
        this.linkFormData = [
          {
            start: null,
            end: null, 
            link: null,
          }
        ]
        this.$store.commit('updateSnackbar', {
          flag: true,
          snackbarMsg: resp.data.message,
          timeout: 3000
        })
        this.files = null
        this.updateVideoDetails(null)

      })
      .catch(() => {
        // console.log(error)
        this.$store.commit('updateSnackbar', {
          flag: true,
          snackbarMsg: 'Sorry, there was a problem!',
          timeout: 3000
        })
      })
    }
  },
};
</script>

<style scoped>


</style>

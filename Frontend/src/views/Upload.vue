<template>
  <v-content>
    <v-row
      align="center"
      justify="center"
    >
      <v-col align="center">
        <v-col>
          <v-file-input
            accept="video/mp4"
            placeholder="mp4 only!"
            label="Select video"
            :show-size="1000"
            @change="getVideoDuration"
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
          <v-snackbar
            v-model="snackbar.flag"
            :timeout="0"
          >
            {{ snackbar.snackbarMsg }}
          </v-snackbar>
        </v-col>
        <v-col>
          <v-btn
            fab
            small
            bottom
            @click="addLink"
          >
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </v-col>
        <v-col>        
          <v-btn
            bottom
            :disabled="!submit"
          >
            Submit
          </v-btn>
        </v-col>
      </v-col>
    </v-row>
  </v-content>
</template>

<script>
export default {

  name: "Upload",
  data: () => ({
    videoDuration: null,
    valid: false,
    linkFormData: [
      {
        start: null,
        end: null, 
        link: null,
      }
    ],
    rules: {
      numRules: v => {
        if (/([0-9]+)/g.test(v)) {
          if (parseInt(v)%10 == 0) return true
          else return "Please enter multiples of 10!"
        }
         else return "Please enter a number!"
      },
      linkRules: v => {
        if (/(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_+.~#?&//=]*)/g.test(v)) {
          return true
        } else return "Not a valid URL!"
      }
    },
  }),
  computed: {
    snackbar: function() {
      const snackbar = {
        flag: false,
        snackbarMsg: null
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
      }

      return snackbar
    },
    tempNumFlag: function() {
      let tempNumFlag = true
      for (let i = 0; i < this.linkFormData.length; i++) {
        let currentLink = this.linkFormData[i]
        // set tempNumFlag if start/end fail rule validation
        if (
          (this.rules.numRules(currentLink.start)!= true) || 
          (this.rules.numRules(currentLink.end) != true)
        ) tempNumFlag = false
      }
      return tempNumFlag
    },
    tempLinkFlag: function() {
      let tempLinkFlag = true
      for (let i = 0; i < this.linkFormData.length; i++) {
        let currentLink = this.linkFormData[i]

        // set tempLinkFlag if link fails validation
        if ((this.rules.linkRules(currentLink.link)) != true) tempLinkFlag = false
      }
      return tempLinkFlag
    },
    submit: function() {
      return (!this.snackbar.flag && this.tempNumFlag && this.tempLinkFlag && this.videoDuration)
    }
  },
  methods: {
    getVideoDuration(file) {
      if (file) {
        const vid = document.createElement('video');
        // create url to use as the src of the video
        const fileURL = URL.createObjectURL(file);
        vid.src = fileURL;
        const that=this
        // wait for duration to change from NaN to the actual duration
        vid.ondurationchange = function() {
          that.videoDuration = Math.round(this.duration);
        };
      }
    },
    addLink() {
      const linkTemplate = {
        start: null,
        end: null, 
        link: "",
      }
      this.linkFormData.push(linkTemplate)
    },
    deleteLink(index) {
      this.linkFormData.splice(index, 1)
    }
  },
};
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

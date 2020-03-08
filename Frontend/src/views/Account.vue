<template>
  <v-container>
    <v-row>
      <v-col align="center">
        <v-col>
          <!-- Account Details Card -->
          <v-card
            class="mx-auto"
            tile
          >
            <v-card-title> Account Details </v-card-title>
            <v-list disabled>
              <v-list-item-group color="primary">
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>{{ `Name: ${$store.state.name}` }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title> {{ `Email: ${$store.state.email}` }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-col>
        <v-col v-if="video_records.length>0">
          <v-data-table
            :headers="headers"
            :items="video_records"
            class="elevation-1"
          >
            <template v-slot:top>
              <v-toolbar flat>
                <v-toolbar-title>Video Details</v-toolbar-title>
              </v-toolbar>
            </template>
            <template v-slot:item.epoch="{ item }">
              <span>{{ new Date(item.epoch * 1000).toLocaleString() }}</span>
            </template>
            <template v-slot:item.links="{ item }">
              <span>{{ item.ultrasounds.length }}</span>
            </template>
            <template v-slot:item.action="{ item }">
              <v-icon
                small
                class="mr-2"
                @click="showVideoDetails(item)"
              >
                mdi-information
              </v-icon>
              <v-btn
                icon
                class="mr-2"
                :href="item.link"
              >
                <v-icon small>
                  mdi-download
                </v-icon>
              </v-btn>
              <v-icon
                small
                color="error"
                @click="deleteVideo(item._id)"
              >
                mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </v-col>
        <v-col>
          <v-btn
            @click="logout"
          >
            Logout
          </v-btn>
        </v-col>
        <v-col>
          <v-btn
            color="error"
            @click="deleteAccount"
          >
            Delete Account
          </v-btn>
        </v-col>
      </v-col>
    </v-row>
    <v-overlay
      v-if="overlay"
      :value="overlay"
    >
      <v-col align="center">
        <v-card
          class="mx-auto"
          raised
        >
          <v-card-title> Video Details </v-card-title>
          <v-list disabled>
            <v-list-item-group color="primary">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title> {{ overlay_video.name }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              <v-list-item
                v-for="ultrasound in overlay_video.ultrasounds"
                :key="ultrasound._id"
                two-line
                ripple
              >
                <v-list-item-content>
                  <v-list-item-title> {{ ultrasound.content }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ `${ultrasound.start} to ${ultrasound.end}` }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
          <v-btn
            icon
            @click="overlay = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card>
      </v-col>
    </v-overlay>
  </v-container>
</template>

<script>
import Axios from '../utilities/api';
export default {
  name: "Account",
  props: {
  },

  data: () => ({
    video_records: [],
    headers: [
      {text: 'Date', align: 'start',value: 'epoch'},
      {text: 'Title', value: 'name'},
      {text: 'Links', value: 'links'},
      { text: 'Actions', value: 'action', sortable: false },
    ],
    overlay: false,
    overlay_video: null
  }),
  mounted() {
    this.getAccountRecords()
  },
  methods: {
    logout() {
      this.$store.commit('resetState')
      this.$router.push('/')
    },
    getAccountRecords() {
      const server_url = process.env.VUE_APP_SERVER_URL
      const jwt = this.$store.state.jwt
      const config = {
        headers: {Authorization: `Bearer ${jwt}`}
      }

      Axios
      .get(`${server_url}/user`, config)
      .then(resp => {
        this.video_records = resp.data.data.map(video => {
          video.epoch = this.objectIdToEpoch(video._id)
          video.link = `${server_url}/get-video/${video.name}`
          video.ultrasounds.forEach(ultrasound => {
            ultrasound.start = this.SStoMM_SS(ultrasound.start)
            ultrasound.end = this.SStoMM_SS(ultrasound.end)
          })
          return video
        })
      })
      .catch(error => {
        if (!error.response) {
          this.$store.commit('updateSnackbar', {
            flag: true,
            snackbarMsg: 'Sorry, there was a network problem!',
            timeout: 3000
          })
        }
        else {
          this.$store.commit('updateSnackbar', {
            flag: true,
            snackbarMsg: 'Sorry, there was a server problem!',
            timeout: 3000
          })
        }
      })
    },
    deleteVideo(_id) {
      const server_url = process.env.VUE_APP_SERVER_URL
      const bodyFormData = new FormData();
      const jwt = this.$store.state.jwt
      const config = {
        headers: {Authorization: `Bearer ${jwt}`}
      }
      bodyFormData.append('video_id', _id)

      Axios
      .post(`${server_url}/delete-video`, bodyFormData, config)
      .then(() => {
        this.video_records = this.video_records.filter((video)=> {
          video._id !== _id
        })
      })
      .catch(error => {
        console.error(error)
      })
    },
    showVideoDetails(video) {
      this.overlay_video = video
      this.overlay = true
    },
    SStoMM_SS(seconds) {
      let date = new Date(null);
      date.setSeconds(seconds);
      let result = date.toISOString()
      if (seconds < 60*60) {
        result = result.substr(14, 5);
      } else result = result.substr(11, 8);
      return result
    },
    objectIdToEpoch(_id) {
      return parseInt(_id.substring(0, 8), 16)
    },
    deleteAccount() {
      const server_url = process.env.VUE_APP_SERVER_URL
      const jwt = this.$store.state.jwt
      const config = {
        headers: {Authorization: `Bearer ${jwt}`}
      }
      Axios
      .delete(`${server_url}/user`, config)
      .then(()=>{
        this.$store.commit('resetState')
        this.$router.push('/')
        this.$store.commit('updateSnackbar', {
          snackbarMsg: 'Account Deleted!',
          flag: true,
          timeout: 3000
        })
      })
    }
  },
};
</script>

<style scoped>
/* Inserting this collapsed row between two flex items will make
* the flex item that comes after it break to a new row */
.break {
  flex-basis: 100%;
  height: 0;
}

</style>
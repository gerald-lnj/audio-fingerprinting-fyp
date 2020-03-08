<template>
  <v-container>
    <v-row>
      <v-col align="center">
        <!-- Account Details Card -->
        <v-col>
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
        <!-- Video Records Table -->
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
                @click="dialog_video = item; delete_dialog = true"
              >
                mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </v-col>
        <!-- Logout Button -->
        <v-col>
          <v-btn
            @click="logout"
          >
            Logout
          </v-btn>
        </v-col>
        <!-- Delete Account Dialog -->
        <v-dialog
          v-model="delete_account_dialog"
          width="500"
        >
          <template v-slot:activator="{ on }">
            <v-btn
              color="error"
              v-on="on"
            >
              Delete Account
            </v-btn>
          </template>

          <v-card>
            <v-card-title> Delete Account ? </v-card-title>
            <v-card-text>
              If you delete your account, all records of videos created by you will be deleted, and you will not be able to run detection on any of them to retrieve metadata!
            </v-card-text>

            <v-divider />

            <v-card-actions>
              <v-spacer />
              <v-btn
                color="error"
                text
                @click="deleteAccount()"
              >
                Delete Account
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
    </v-row>
    <!-- Video Info Dialog -->
    <v-dialog
      v-model="info_dialog"
      width="500"
    >
      <v-card
        v-if="info_dialog"
        class="mx-auto"
        raised
      >
        <v-card-title> {{ dialog_video.name }} </v-card-title>
        <v-list disabled>
          <v-list-item-group color="primary">
            <v-list-item
              v-for="ultrasound in dialog_video.ultrasounds"
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
        <v-card-actions>
          <v-spacer />
          <v-btn
            icon
            @click="info_dialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Video Dialog -->
    <v-dialog
      v-model="delete_dialog"
      width="500"
    >
      <v-card
        v-if="delete_dialog"
        class="mx-auto"
        raised
      >
        <v-card-title> Delete {{ dialog_video.name }} ? </v-card-title>
        <v-card-text>
          Deleting only removes fingerprints from our database. You can stil play your videos, but you won't be able to retieve metadata though our detection!
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            text
            color="error"
            @click="deleteVideo(dialog_video._id); delete_dialog=false"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
      {text: 'Actions', value: 'action', sortable: false},
    ],
    dialog_video: null,
    info_dialog: false,
    delete_dialog: false,
    delete_account_dialog: false
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
        this.getAccountRecords()
      })
      .catch(error => {
        console.error(error)
      })
    },
    showVideoDetails(video) {
      this.dialog_video = video
      this.info_dialog = true
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
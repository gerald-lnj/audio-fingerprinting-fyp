<template>
  <v-app>
    <!-- nav drawer -->
    <v-navigation-drawer
      v-model="drawer"
      app
    >
      <v-list dense>
        <v-list-item
          to="/"
          link
        >
          <v-list-item-action>
            <v-icon>mdi-home</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              Home
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item
          to="detect"
          link
        >
          <v-list-item-action>
            <v-icon>mdi-microphone</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              Detect
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item
          @click="uploadLoginChecker"
        >
          <v-list-item-action>
            <v-icon>mdi-upload</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Upload</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item
          to="about"
          link
        >
          <v-list-item-action>
            <v-icon>mdi-information</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              About
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- nav bar -->
    <v-app-bar
      app
      color="#003459"
      dark
    >
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title>Link Embedder</v-toolbar-title>
      <v-spacer />
      <v-dialog
        v-if="this.$route.meta.helpText"
        v-model="help"

        width="500"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            icon
            v-on="on"
          >
            <v-icon>
              mdi-help-circle
            </v-icon>
          </v-btn>
        </template>

        <v-card>
          <v-card-title primary-title>
            Help
          </v-card-title>

          <v-card-text>
            <div
              v-for="(text, index) in this.$route.meta.helpText.split('\n')"
              :key="index"
            >
              {{ text }}
            </div>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              text
              @click="help = false"
            >
              Dismiss
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-btn
        icon
        :disabled="this.$route.meta.hideButton"
        :to="appBarBtnDest"
        active-class
      >
        <v-icon>
          mdi-account-circle
        </v-icon>
      </v-btn>
    </v-app-bar>


    <v-content>
      <!-- Provides the application the proper gutter -->
      <v-container 
        fluid
        fill-height
      >
        <!-- for vue-router -->
        <router-view />
      </v-container>
    </v-content>

    <v-snackbar
      v-model="$store.state.snackbar.flag"
      :timeout="$store.state.snackbar.timeout"
    >
      {{ $store.state.snackbar.snackbarMsg }}
    </v-snackbar>
  </v-app>
</template>

<script>
export default {
  name: 'App',
  props: {
  },
  data: () => ({
    help: false,
    drawer: false,
    snackbar: false,
  }),
  computed: {
    buttonText() {
      return this.$store.state.loggedIn ? "Account" : "Login"
      },
    appBarBtnDest() {
      return this.$store.state.loggedIn ? 'account' : 'login'
    }
  },
  mounted() {
    this.$store.commit('updateWindowWidth', window.innerWidth)
    window.onresize = () => {
      this.$store.commit('updateWindowWidth', window.innerWidth)
    }
  },
  methods: {
    uploadLoginChecker() {
      if (this.$store.state.loggedIn) this.$router.push('upload')
      else {
        this.$store.commit('updateSnackbar', {
          flag: true,
          snackbarMsg: 'Login required!',
          timeout: 3000
        })
        this.$router.push('login')
      }
    },
  }
};
</script>

<style>
</style>

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
      </v-list>
    </v-navigation-drawer>

    <!-- nav bar -->
    <v-app-bar
      app
      color="#003459"
      dark
    >
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title>Fingerprinting</v-toolbar-title>
      <v-layout
        align-end
        justify-end
      >
        <v-btn
          colour="indigo"
          :disabled="this.$route.meta.hideButton"
          :to="appBarBtnDest"
        >
          {{ buttonText }}
        </v-btn>
      </v-layout>
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
      :timeout="3000"
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
    drawer: false,
    snackbar: false

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
      if (this.$store.state.loggedIn) {
        this.$router.push('upload')
      } else {
        this.$store.state.snackbar.snackbarMsg = 'Login required!';
        this.$store.state.snackbar.flag = true;
      }
    },
  }
};
</script>

<style>
</style>

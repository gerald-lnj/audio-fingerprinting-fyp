<template>
  <v-container>
    <v-row>
      <v-col align="center">
        <v-col>
          <v-img
            src="@/assets/logo.png"
            aspect-ratio="1"
            max-height="100"
            contain
          />
        </v-col>
        <v-col>
          <v-btn
            to="detect"
          > 
            DETECT 
          </v-btn>
        </v-col>

        <v-col>
          <v-btn
            @click="uploadLoginChecker"
          >
            UPLOAD
          </v-btn>
        </v-col>

        <v-col v-if="false">
          <v-btn
            @click="resetState"
          > 
            RESET STATE 
          </v-btn>
        </v-col>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'Home',
  props: {
  },
  data: () => ({
  }),
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
    resetState() {
      this.$store.commit('resetState')
    }
  }
};
</script>

<style scoped>

</style>
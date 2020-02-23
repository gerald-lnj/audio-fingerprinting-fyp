<template>
  <v-container>
    <v-row>
      <v-col align="center">
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

        <v-col>
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
        this.$store.state.snackbar.snackbarMsg = 'Login Required!'
        this.$store.state.snackbar.flag = true
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
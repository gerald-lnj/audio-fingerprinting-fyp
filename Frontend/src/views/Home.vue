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
            @click="debug"
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
    debug() {
      this.$store.commit('resetState')
    }
  }
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
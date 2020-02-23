<template>
  <v-container>
    <v-row>
      <v-col align="center">
        <v-col>
          <v-form v-model="valid">
            <v-container>
              <v-row>
                <v-text-field
                  v-model="name"
                  label="Name"
                  required
                />
              </v-row>
              <v-row>
                <v-text-field
                  v-model="email"
                  label="Email"
                  required
                  :rules="[rules.emailRules]"
                />
              </v-row>
              <v-row>
                <v-text-field
                  v-model="password"
                  label="Password"
                  required
                  :rules="[rules.passwordRules]"
                />
              </v-row>
            </v-container>
          </v-form>
        </v-col>

        <v-col>
          <v-btn
            :disabled="!valid"
            @click="postRegister"
          >
            Register
          </v-btn>
        </v-col>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Axios from '../utilities/api';

export default {
  name: 'Register',
  props: {
  },
  data: () => ({
    valid: false,
    name: '',
    email: '',
    password: '',
    rules: {
      passwordRules: v => {
        if (v.length >= 8) return true
        else return 'At least 8 characters!'
      },
      emailRules: v=> {
        if (/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v)) return true
        else return 'Not a valid email!'
      }
    },
  }),
  methods: {
    postRegister() {
      const server_url = process.env.VUE_APP_SERVER_URL
      const bodyFormData = new FormData();
      bodyFormData.set('name', this.name)
      bodyFormData.set('email', this.email)
      bodyFormData.set('password', this.password)
      
      Axios
      .post(`${server_url}/register`, bodyFormData)
      .then(()=> {
        this.$store.state.snackbar.snackbarMsg = 'Success!'
        this.$store.state.snackbar.flag = true
        this.$router.push('login')
      })
      .catch(error => {
        const statusCode = error.response.status
        switch (statusCode) {
          case 409:
            // email already exists
            this.$store.state.snackbar.snackbarMsg = 'User with this email already exists!'
            this.$store.state.snackbar.flag = true
            break;
        
          default:
            // 500 (internal server)
            // 400 (bad req params)
            this.$store.state.snackbar.snackbarMsg = 'Sorry, we encountered an error. Try again later!'
            this.$store.state.snackbar.flag = true
            break;
        }
      })
    }
  }
};
</script>

<style scoped>

</style>
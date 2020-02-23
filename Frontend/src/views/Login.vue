<template>
  <v-row>
    <v-col align="center">
      <v-col>
        <v-form>
          <v-container>
            <v-text-field
              v-model="email"
              :rules="[rules.required, rules.email]"
              autocomplete="email"
              label="Email"
            />
            <v-text-field
              v-model="password"
              :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              :rules="[rules.required]"
              :type="showPassword ? 'text' : 'password'"
              name="input-10-1"
              label="Password"
              hint="At least 8 characters"
              counter
              autocomplete="password"
              @click:append="showPassword = !showPassword"
            />
          </v-container>
        </v-form>
      </v-col>

      <v-col>
        <v-btn
          class="button mt-3 mv-5"
          variant="warning" 
          pill 
          @click="login"
        >
          Login
        </v-btn>
      </v-col>
      <v-col>
        <p class="mt-3 mv-0 text-white">
          No Account?
          <br>
        </p>
        <v-btn
          to="/sign-up"
        >
          Sign Up Here
        </v-btn>
      </v-col>
      <v-col>
        <v-btn
          @click="onPasswordReset"
        >
          Forgot your password?
        </v-btn>
      </v-col>
    </v-col>
  </v-row>
</template>

<script>
import Axios from "../utilities/api";
export default {

  name: "Login",
  data: () => ({
    email: "",
    password: "",
    showPassword: false,
    rules: {
      required (value) {
        return !!value||'Required'
      },
      email (value) {
        const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        return pattern.test(value) || 'Invalid e-mail.'
      },
    },

  }),
  methods: {
    login() {
      // const data = {
      //   "email": this.email,
      //   "password": this.password
      // }
      const data = {
        "email": 'test@test.com',
        "password": '12345'
      }
      const server_url = process.env.VUE_APP_SERVER_URL
      Axios.post(`${server_url}/auth`, data)
      .then((resp)=> {
        this.$store.commit('updateDetails', resp)
        this.$store.commit('updateLoginStatus')
        this.$router.push('/')
      })
      .catch((error)=>{
        console.log(error)
      })



    },
    onPasswordReset() {
      this.$store.state.snackbar.snackbarMsg = 'Sorry, we don\'t have the resources to implement password reset at this time!'
      this.$store.state.snackbar.flag = true
    },

    onSubmitResetPassword() {
      // tbc
    }


  },
};
</script>

<style scoped>


</style>

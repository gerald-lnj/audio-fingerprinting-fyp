<template>
  <v-container 
    fill-height 
    fluid
  >
    <v-row
      align="center"
      justify="center"
    >
      <v-card
        class="mx-auto"
        max-width="300"
        tile
      >
        <v-list disabled>
          <v-subheader>Account Details</v-subheader>
          <v-list-item-group color="primary">
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title>{{ name }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title> {{ email }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-card>
      <div class="break" />
      <p class="mt-3 mv-0 text-white">
        <v-btn
          @click="logout"
        >
          Logout
        </v-btn>
      </p>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "Account",
  props: {
  },

  data: () => ({

  }),
  computed: {
    name() {return `Name: ${this.$store.state.name}`},
    email() {return `Email: ${this.$store.state.email}`}
  },
  methods: {
    logout() {
      this.$store.commit('resetState')
      this.$router.push('/')
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
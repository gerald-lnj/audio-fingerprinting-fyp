<template>
  <v-container>
    <v-row>
      <body>
        <p class="headline text-primary">
          What is this app?
        </p>
        <p class="font-weight-light">
          This is the Audio Fingerprinting application.<br>
          It was created by Gerald Lau as his Final Year Project in NTU.
        </p>
        <br>

        <p class="headline text-primary">
          What can it do?
        </p>
        <p class="font-weight-light">
          This application embeds data into the audio of a video, via the Upload page.<br>
          You can then play the video, and the app will passively listen to the audio and retrieve data that has been embedded into it.
        </p>
        <br>

        <p class="headline text-primary">
          What's the difference between Fingerprinting and Watermarking?
        </p>
        <p class="font-weight-light">
          Fingerprinting and Watermarking are the two modes of embedding data into the video.<br>
          Our implementation of it uses similar technologies, but applied in a different way.
        </p>
        <p class="title text-primary">
          Fingerprinting
        </p>
        <p class="font-weight-light">
          The Fingerprinting mode listens to the video's audio, and generates unique identifiers called fingeprints.<br>
          A link and the associated fingerprints are stored in our database.<br>
          By playing back the original video, and comparing fingeprints, a match is found.
        </p>
        <p class="title text-primary"> 
          Watermarking
        </p>
        <p class="font-weight-light">
          The Watermarking mode uses the link to be embedded as a seed to generate random ultrasound.<br>
          This ultrasound is embedded into the video's audio track.<br>
          A link and the associated fingerprints from the ultrasound are stored in our database.<br>
          By downloading the modified video, playing it back and comparing fingeprints, a match is found.
        </p>
        <p class="title text-primary"> 
          Which should I use?
        </p>
        <p class="font-weight-light">
          Fingerprinting is more convienient, as it works without modification of the original video.<br>
          Watermarking requires that you distribute the modified video.<br>
          However, the accuracy of Watermarking is superior.
        </p>
        <p class="font-weight-light">
          If you are trying to retrieve links via the Detect page, make sure that you have selected the same mode that the links were embedded with!
        </p>
      </body>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'About',
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
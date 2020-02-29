import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from "vuex-persistedstate";


Vue.use(Vuex);

export default new Vuex.Store({
  plugins: [createPersistedState()],
  state: {
    loggedIn: false,
    name: '',
    email: '',
    refresh: '',
    jwt: '',
    snackbar: {
      flag: false,
      snackbarMsg: ''
    }
  },
    windowWidth: null
  mutations: {
    updateDetails(state, resp) {
      state.email=resp.data.data.email
      state.name=resp.data.data.name
      state.refresh=resp.data.data.refresh
      state.jwt=resp.data.data.token
    },
    updateLoginStatus(state) {
      state.loggedIn = state.email.length > 0
    },
    resetState(state) {
      Object.assign(state, getDefaultState())
    },
    updateWindowWidth(state, windowWidth) {
      state.windowWidth = windowWidth
    },
    }
  },
  actions: {
  },
  modules: {
  },
});

const getDefaultState= () => {
  return {
    loggedIn: false,
    name: '',
    email: '',
    refresh: '',
    jwt: '',
    snackbar: {
      flag: false,
      snackbarMsg: ''
    }
    windowWidth: null
  }
}

import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    loggedIn: false,
    name: '',
    email: '',
    refresh: '',
    jwt: '',
  },
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
      console.log(state)
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
  }
}

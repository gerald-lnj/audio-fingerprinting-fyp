import Axios from "axios";
import createAuthRefreshInterceptor from 'axios-auth-refresh';
import router from '../router';
import store from '../store'

// interceptor logic to get new access token using refresh token
const refreshAuthLogic = failedRequest => {
  const refresh = store.state.refresh
  const config = {
    headers: {Authorization: `Bearer ${refresh}`}
  }
  return Axios
  .post(`${process.env.VUE_APP_SERVER_URL}/refresh`, {}, config)
  .then(tokenRefreshResponse => {
    store.state.jwt = tokenRefreshResponse.data.access_token
    failedRequest.response.config.headers['Authorization'] = `Bearer ${tokenRefreshResponse.data.access_token}`;
    return Promise.resolve();
  })
  .catch(() => {
    store.state.snackbar.snackbarMsg = 'Session expired!'
    store.state.snackbar.flag = true
    router.push('login')
  })
}

createAuthRefreshInterceptor(Axios, refreshAuthLogic);

export default Axios

import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '../store/index'

const Home = r => require.ensure([], () => r(require('../views/Home.vue')))
const Login = r => require.ensure([], () => r(require('../views/Login.vue')))
const Account = r => require.ensure([], () => r(require('../views/Account.vue')))
const Upload = r => require.ensure([], () => r(require('../views/Upload.vue')))
const Detect = r => require.ensure([], () => r(require('../views/Detect.vue')))
const Register = r => require.ensure([], () => r(require('../views/Register.vue')))
const About = r => require.ensure([], () => r(require('../views/About.vue')))
const NotFound = r => require.ensure([], () => r(require('../components/NotFound.vue')))

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: {
      helpText: 
        'Welcome to the Audio Fingerprinting App!\n\
        This app allows you to embed links into videos via the Upload page,\n\
        and retrieve embedded links via the Detect page.\n\
        You can also view your account details and videos in the Account Page!\n\
        Click on this information button on each page for more details on how to use them!',
    }
  },
  {
    path: '/about',
    name: 'about',
    component: About,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      hideButton: true,
      helpText: 
        'This is the login page.\n\
        Please ensure that your password has a minimum length of 8 characters!'
    }
  },
  {
    path: '*',
    name: 'NotFound',
    component: NotFound,
  },
  {
    path: '/account',
    name: 'Account',
    component: Account,
    meta: {
      requiresAuth: true,
      hideButton: true,
      helpText: 
        'This is your account summary page.\n\
        Here, you can check your account information, and see your past video records!\n\
        You can also delete individual video records, or delete your account.\n\
        Deleting a video removes the records from our database, and the videos can still be used as normal.\n\
        Deleting your account will also remove all video records associated with your account!'
    }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload,
    meta: {
      requiresAuth: true,
      helpText: 
        'This is the Upload page.\n\
        Here, you can upload videos, and specify the links to be embedded at specific timestamps.\n\
        There is a simple interface that allows you to insert links at the current video cursor time.\n\
        Below, you can also manually input or edit the links!\n\
        You can only submit the video if it passes all checks!\n\
        If you select Fingerprinting mode, links can only be 20 seconds long.\n\
        Refer to the About page in the sidebar for details on Fingerprinting vs Watermarking.'
    }
  },
  {
    path: '/detect',
    name: 'Detect',
    component: Detect,
    meta: {
      helpText: 
        'This is the Detect page.\n\
        Here, you can retrieve embedded links from video by playing the video.\n\
        Simply tap on the microphone to start, and tap again to stop. Make sure that the audio can be detected by your device\'s microphone!\n\
        Refer to the About page in the sidebar for details on Fingerprinting vs Watermarking.'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      helpText: 
        'This is the Register page.\n\
        Quite straightforward!'
    }
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const loggedIn = store.state.loggedIn
  if (requiresAuth && !loggedIn) {
    next('/login');
  }
  else if (to.path == "/login") {
    if (!loggedIn) next()
  }
  else next();
});

export default router;

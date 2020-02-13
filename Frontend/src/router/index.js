import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '../views/Home.vue';
import NotFound from '../components/NotFound.vue';
import Login from '../views/Login.vue';
import Account from '../views/Account.vue'
import store from '../store/index'
import Upload from '../views/Upload.vue'
import Detect from '../views/Detect.vue'

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      hideButton: true
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
    }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload,
    meta: {
      requiresAuth: true,
    }
  },
  {
    path: '/detect',
    name: 'Detect',
    component: Detect,
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

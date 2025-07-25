import Vue from 'vue';
import VueRouter from 'vue-router';
import login from '../pages/login/login.vue';
import history from '../pages/history/history.vue';
import FAQ from '../pages/FAQ/FAQ.vue';
import profile_update from '../pages/profile_update/profile_update.vue';
import history_carryout from '../pages/history_carryout/history_carryout.vue';
import main_top from '../pages/main_top/main_top.vue';
import DataHub from '@/pages/Datahub/Datahub.vue';


Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'login',
    component: login,
  },
  {
    path: '/history',
    name: 'history',
    component: history,
  },
  {
    path: '/FAQ',
    name: 'FAQ',
    component: FAQ,
  },
  {
    path: '/profile_update',
    name: 'profile_update',
    component: profile_update,
  },
  {
    path: '/history_carryout/:caseId',
    name: 'history_carryout',
    component: history_carryout,
  },
  {
    path: '/main_top',
    name: 'main_top',
    component: main_top,
  },
  {
  path: '/Datahub',
  name: 'Datahub',
  component: DataHub
}
  
  
  
];

const router = new VueRouter({
  mode: 'hash',
  base: process.env.BASE_URL,
  routes,
});

export default router;
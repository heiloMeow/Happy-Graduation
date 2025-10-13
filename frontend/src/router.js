import { createRouter, createWebHistory } from 'vue-router';
import Welcome from './views/Welcome.vue';
import SeatSelect from './views/SeatSelect.vue';
import StatusSelect from './views/StatusSelect.vue';
import Avatar from './views/Avatar.vue';
import Signal from './views/Signal.vue';
import Table from './views/Table.vue';
import Nearby from './views/Nearby.vue';
import SelectPerson from './views/SelectPerson.vue';
import Notify from './views/Notify.vue';

const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: Welcome,
  },
  {
    path: '/seat-select',
    name: 'SeatSelect',
    component: SeatSelect,
  },
  {
    path: '/status-select',
    name: 'StatusSelect',
    component: StatusSelect,
  },
  {
    path: '/avatar',
    name: 'Avatar',
    component: Avatar,
  },
  {
    path: '/signal',
    name: 'Signal',
    component: Signal,
  },
  {
    path: '/table/:id',
    name: 'Table',
    component: Table,
  },
  {
    path: '/nearby',
    name: 'Nearby',
    component: Nearby,
  },
  {
    path: '/select-person/:tableId',
    name: 'SelectPerson',
    component: SelectPerson,
  },
  {
    path: '/notify/:tableId/:userId',
    name: 'Notify',
    component: Notify,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;


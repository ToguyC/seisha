import Archers from '@/views/admin/Archers.vue'
import SingleTournament from '@/views/admin/SingleTournament.vue'
import Tournaments from '@/views/admin/Tournaments.vue'
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: HomeView,
    },
    {
      path: '/admin',
      children: [
        { path: 'archers', component: Archers },
        { path: 'tournaments', component: Tournaments },
        { path: 'tournaments/:id', name: 'singleTournament', component: SingleTournament },
      ],
    },
  ],
})

export default router

import Archers from '@/views/admin/Archers.vue'
import SingleTournament from '@/views/admin/SingleTournament.vue'
import Tournaments from '@/views/admin/Tournaments.vue'
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LiveMatches from '@/views/embed/LiveMatches.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: HomeView,
      meta: { title: 'Home' },
    },
    {
      path: '/embed/live-matches/:id/:matchIdx',
      name: 'embed-live-matches',
      component: LiveMatches,
      meta: { title: 'Live Matches' },
    },
    {
      path: '/admin',
      children: [
        { path: 'archers', component: Archers, meta: { title: 'Archers' } },
        { path: 'tournaments', component: Tournaments, meta: { title: 'Tournaments' } },
        {
          path: 'tournaments/:id',
          name: 'singleTournament',
          component: SingleTournament,
          meta: { title: 'Tournament Details' },
        },
      ],
      meta: { title: 'Admin' },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const defaultTitle = 'Seisha - Archery Tournament Management'
  document.title = to.meta.title ? `${to.meta.title} - Seisha` : defaultTitle
  next()
})

export default router

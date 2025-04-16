<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/base'
import type { Tournament } from '@/models/models'
import Breadcrumb from '@/components/Breadcrumb.vue'

const route = useRoute()

const levels = ref([
  {
    name: 'Admin',
    url: '/',
  },
  {
    name: 'Tournaments',
    url: '/admin/tournaments',
  },
])

const tournament = ref<Tournament>({
  id: 0,
  name: '',
  date: '',
  archers: [],
})

onMounted(() => {
  const tournamentId = route.params.id

  api
    .get(`/tournaments/${tournamentId}`)
    .then((res) => {
      tournament.value = res.data
      levels.value.push({
        name: res.data.name,
        url: `/admin/tournaments/${res.data.id}`,
      })
    })
    .catch((err) => {
      console.error(err.message)
    })
})
</script>

<template>
  <Breadcrumb :levels="levels"></Breadcrumb>
  
  {{ tournament }}
</template>

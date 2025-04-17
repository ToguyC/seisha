<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/base'
import type { Tournament } from '@/models/models'
import Breadcrumb from '@/components/Breadcrumb.vue'
import { PlusIcon } from '@heroicons/vue/16/solid'

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
  start_date: '',
  end_date: '',
  format: '',
  status: '',
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

  <div class="flex flex-col w-full items-center justify-center my-10">
    <div class="text-4xl font-bold">{{ tournament.name }}</div>
  </div>

  <table class="w-full">
    <tbody>
      <tr>
        <td class="w-40 font-semibold p-1 bg-gray-200">Start date</td>
        <td class="px-3">{{ new Date(tournament.start_date).toLocaleDateString() }}</td>
        <td class="w-40 font-semibold p-1 bg-gray-200">End date</td>
        <td class="px-3">{{ new Date(tournament.end_date).toLocaleDateString() }}</td>
        <td class="w-40 font-semibold p-1 bg-gray-200">Format</td>
        <td class="px-3">
          <div
            v-if="tournament.format === 'individual'"
            class="bg-emerald-100 text-emerald-700 font-semibold w-10 rounded-sm flex items-center justify-center"
          >
            個人
          </div>
          <div
            v-else
            class="bg-purple-100 text-purple-700 font-semibold w-12 rounded-sm flex items-center justify-center"
          >
            チーム
          </div>
        </td>
      </tr>
    </tbody>
  </table>

  <div class="flex items-center gap-4 my-10">
    <div v-if="tournament.status === 'upcoming'" class="w-6 h-6 bg-orange-400 rounded-full"></div>
    <div v-if="tournament.status === 'live'" class="w-6 h-6 bg-amaranth-500 rounded-full"></div>
    <div v-if="tournament.status === 'finished'" class="w-6 h-6 bg-wedgeblue-500 rounded-full"></div>
    <div v-if="tournament.status === 'cancelled'" class="w-10 h-10">
      <PlusIcon class="w-full h-full rotate-45 text-amaranth-500" />
    </div>
    <div class="uppercase font-bold text-3xl">{{ tournament.status }}</div>
  </div>

  <div>
    <div class="text-xl font-bold text-gray-900">Archers</div>
  </div>
  {{ tournament }}
</template>

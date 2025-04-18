<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/base'
import type { Tournament } from '@/models/models'
import Breadcrumb from '@/components/Breadcrumb.vue'
import { HashtagIcon, PlusIcon } from '@heroicons/vue/16/solid'

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
  teams: [],
  matches: [],
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

  <table class="w-full mb-5">
    <tbody>
      <tr>
        <td class="w-40 font-semibold p-1 bg-gray-200 text-center">Start date</td>
        <td class="px-3">{{ new Date(tournament.start_date).toLocaleDateString() }}</td>
        <td class="w-40 font-semibold p-1 bg-gray-200 text-center">End date</td>
        <td class="px-3">{{ new Date(tournament.end_date).toLocaleDateString() }}</td>
        <td class="w-40 font-semibold p-1 bg-gray-200 text-center">Format</td>
        <td class="px-3">
          <div
            v-if="tournament.format === 'individual'"
            class="bg-emerald-100 text-emerald-700 font-semibold w-12 rounded-sm flex items-center justify-center"
          >
            個人
          </div>
          <div
            v-else
            class="bg-purple-100 text-purple-700 font-semibold w-16 rounded-sm flex items-center justify-center"
          >
            チーム
          </div>
        </td>
        <td class="w-40 font-semibold p-1 bg-gray-200 text-center">Status</td>
        <td class="px-3">
          <div
            v-if="tournament.status === 'upcoming'"
            class="bg-orange-100 text-orange-700 font-semibold w-20 rounded-sm flex items-center justify-center"
          >
            開催前
          </div>
          <div
            v-else-if="tournament.status === 'live'"
            class="bg-amaranth-500 text-white font-semibold w-20 rounded-sm flex items-center justify-center gap-2"
          >
            <div class="w-2 h-2 rounded-full bg-white"></div> 開催中
          </div>
          <div
            v-else-if="tournament.status === 'finished'"
            class="bg-wedgeblue-100 text-wedgeblue-700 font-semibold w-20 rounded-sm flex items-center justify-center"
          >
            終了
          </div>
          <div
            v-else-if="tournament.status === 'cancelled'"
            class="bg-red-100 text-red-700 font-semibold w-20 rounded-sm flex items-center justify-center"
          >
            中止
          </div>
        </td>
      </tr>
    </tbody>
  </table>

  <div class="w-full h-1 border-b border-gray-200 mb-5"></div>

  <div class="flex flex-col gap-4">
    <div class="w-1/2">
      <div class="text-xl font-bold text-gray-900 capitalize mb-6">{{ tournament.format }}</div>

      <div v-if="tournament.format === 'teams'" class="flex w-full items-center gap-6">
        <table class="w-full text-sm text-left rtl:text-right text-gray-500">
          <thead class="text-xs text-gray-500 uppercase bg-gray-50">
            <tr class="font-bold">
              <td class="px-6 py-3"><HashtagIcon class="w-4 h-4" /></td>
              <td class="px-6 py-3">Name</td>
              <td class="px-6 py-3">Archers</td>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(team, index) in tournament.teams"
              :key="index"
              class="bg-white border-b border-gray-200 hover:bg-gray-50 hover:cursor-pointer group"
            >
              <td class="px-6 py-4 w-4 text-gray-900 whitespace-nowrap font-semibold">{{ team.id }}</td>
              <td scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">{{ team.name }}</td>

              <td class="px-6 py-4 w-4 flex flex-col items-center gap-2 text-gray-900 capitalize">
                <div v-for="(archer, idx) in team.archers" :key="idx">
                  {{ archer.name }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else>
        <table class="w-full text-sm text-left rtl:text-right text-gray-500">
          <thead class="text-xs text-gray-500 uppercase bg-gray-50">
            <tr class="font-bold">
              <td class="px-6 py-3"><HashtagIcon class="w-4 h-4" /></td>
              <td class="px-6 py-3">Name</td>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(archer, index) in tournament.archers"
              :key="index"
              class="bg-white border-b border-gray-200 hover:bg-gray-50 hover:cursor-pointer group"
            >
              <td class="px-6 py-4 w-4 text-gray-900 whitespace-nowrap font-semibold">{{ archer.id }}</td>
              <td scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">{{ archer.name }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

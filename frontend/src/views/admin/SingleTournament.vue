<script setup lang="ts">
import { getTournament } from '@/api/tournament'
import Breadcrumb from '@/components/Breadcrumb.vue'
import ArchersList from '@/components/single-tournament/ArchersList.vue'
import SingleTournamentHeader from '@/components/single-tournament/Header.vue'
import Matches from '@/components/single-tournament/Matches.vue'
import TeamsList from '@/components/single-tournament/TeamsList.vue'
import type { TournamentWithRelations } from '@/models/models'
import { PlusIcon } from '@heroicons/vue/16/solid'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const tournament = ref<TournamentWithRelations>({
  id: 0,
  name: '',
  start_date: '',
  end_date: '',
  format: '',
  status: '',
  target_count: 0,
  archers: [],
  teams: [],
  matches: [],
})

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

const fetchTournament = (tournamentId: number) => {
  getTournament(tournamentId)
    .then((res) => {
      tournament.value = res.data

      levels.value = levels.value.filter((level) => level.name !== tournament.value.name)
      levels.value.push({
        name: tournament.value.name,
        url: `/admin/tournaments/${tournamentId}`,
      })
    })
    .catch((err) => {
      console.error(err.message)
    })
}

onMounted(() => {
  const tournamentId = route.params.id

  if (tournamentId) {
    fetchTournament(Number(tournamentId))
  } else {
    console.error('Tournament ID is required')
  }
})
</script>

<template>
  <Breadcrumb :levels="levels"></Breadcrumb>

  <SingleTournamentHeader
    :tournament="tournament"
    class="my-10"
    @fetch-tournament="fetchTournament"
  />

  <div class="w-full h-1 border-b border-gray-200"></div>

  <div class="flex gap-10">
    <div class="w-1/2 py-5">
      <ArchersList
        v-if="tournament.format === 'individual'"
        :tournament="tournament"
        @fetch-tournament="fetchTournament"
      />
      <TeamsList v-else :tournament="tournament" @fetch-tournament="fetchTournament" />
    </div>

    <div class="border-r border-gray-200"></div>

    <div class="w-1/2 py-5">
      <Matches :tournament="tournament" @fetch-tournament="fetchTournament" />
    </div>
  </div>
</template>

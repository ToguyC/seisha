<script setup lang="ts">
import { getTournament, postTournamentMatch, putTournament } from '@/api/tournament'
import Breadcrumb from '@/components/Breadcrumb.vue'
import Overview from '@/components/Overview.vue'
import ArchersList from '@/components/single-tournament/ArchersList.vue'
import SingleTournamentHeader from '@/components/single-tournament/Header.vue'
import Matches from '@/components/single-tournament/Matches.vue'
import TeamsList from '@/components/single-tournament/TeamsList.vue'
import type { Archer, ArcherWithNumber, Team, TournamentWithRelations } from '@/models/models'
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
  advancing_count: 0,
  current_stage: '',
  created_at: '',
  updated_at: '',
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
const tabs = ref(['Participants', 'Qualifiers', 'Finals'])
const activeTab = ref(tabs.value[0])

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

const isTournamentOnlyFinals = (tournament: TournamentWithRelations) => {
  return (
    tournament.current_stage === 'finals' &&
    tournament.matches.filter((m) => m.stage === 'qualifiers').length == 0
  )
}

const generateNextMatch = () => {
  postTournamentMatch(tournament.value.id)
    .then((res) => {
      fetchTournament(tournament.value.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const getHitCount = (archer: Archer, stage: 'qualifiers' | 'finals') => {
  const allSeries = tournament.value.matches
    .filter((match) => match.stage === stage)
    .flatMap((match) => match.series)
    .filter((series) => series.archer.id === archer.id)

  const { hits, total } = allSeries.reduce(
    ({ hits, total }, series) => {
      const arrows = JSON.parse(series.arrows_raw) as number[]
      return { hits: hits + arrows.filter((a) => a === 1).length, total: total + arrows.length }
    },
    { hits: 0, total: 0 },
  )

  return [hits, total, hits / total || 0]
}

const getTeamHitCount = (team: Team, stage: 'qualifiers' | 'finals') => {
  const { hits, total } = team.archers.reduce(
    (acc, a) => {
      const [archerHits, archerTotal] = getHitCount(a.archer, stage)
      acc.hits += archerHits
      acc.total += archerTotal
      return acc
    },
    { hits: 0, total: 0 },
  )

  return [hits, total, hits / total || 0]
}

const terminateQualifiers = () => {
  if (
    !confirm(
      'Are you sure you want to terminate the qualifiers? This will end all qualifier rounds. This action cannot be undone.',
    )
  ) {
    return
  }

  // putTournament({
  //   ...tournament.value,
  //   current_stage: 'finals',
  // })
  //   .then((res) => {
  //     fetchTournament(tournament.value.id)
  //   })
  //   .catch((err) => {
  //     console.error(err.message)
  //   })

  type WithHitCount<T> = T & { hit_count: number[] }
  let sortedParticipants: WithHitCount<Team | ArcherWithNumber>[] = []

  if (tournament.value.format === 'individual') {
    sortedParticipants = tournament.value.archers
      .map((archer) => ({
        ...archer,
        hit_count: getHitCount(archer.archer, 'qualifiers'),
      }))
      .sort((a, b) => b.hit_count[0] - a.hit_count[0])
  } else {
    sortedParticipants = tournament.value.teams
      .map((team) => ({
        ...team,
        hit_count: getTeamHitCount(team, 'qualifiers'),
      }))
      .sort((a, b) => b.hit_count[0] - a.hit_count[0])
  }

  const cutoffIndex = tournament.value.advancing_count - 1
  const cutoffHitCount = sortedParticipants[cutoffIndex]?.hit_count[0] ?? -1

  const advancingTeams = sortedParticipants.filter((p) => p.hit_count[0] >= cutoffHitCount)
  const isTieBreakerNeeded = advancingTeams.length > tournament.value.advancing_count

  console.log('Advancing Teams:', advancingTeams)
  console.log('Advancing Count:', advancingTeams.length, '/', tournament.value.advancing_count)
  console.log('Is Tie Breaker Needed:', isTieBreakerNeeded)
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

  <div class="flex gap-6 w-full border-b border-gray-200">
    <div
      class="px-2 py-4 border-b-2 border-white text-gray-600 font-medium hover:border-b-gray-400 hover:cursor-pointer hover:text-black"
      :class="{
        '!border-b-amaranth-400 !text-amaranth-400': activeTab === tabs[0],
      }"
      @click="activeTab = tabs[0]"
    >
      Participants
    </div>
    <div
      class="px-2 py-4 border-b-2 border-white text-gray-600 font-medium hover:border-b-gray-400 hover:cursor-pointer hover:text-black"
      :class="{
        '!border-b-amaranth-400 !text-amaranth-400': activeTab === tabs[1],
      }"
      @click="activeTab = tabs[1]"
      v-if="!isTournamentOnlyFinals(tournament)"
    >
      Qualifiers
    </div>
    <div
      class="px-2 py-4 border-b-2 border-white text-gray-600 font-medium hover:border-b-gray-400 hover:cursor-pointer hover:text-black"
      :class="{
        '!border-b-amaranth-400 !text-amaranth-400': activeTab === tabs[2],
      }"
      @click="activeTab = tabs[2]"
      v-if="tournament.current_stage === 'finals'"
    >
      Finals
    </div>
  </div>

  <div class="flex">
    <div class="w-full py-5" v-if="activeTab === 'Participants'">
      <ArchersList
        v-if="tournament.format === 'individual'"
        :tournament="tournament"
        @fetch-tournament="fetchTournament"
      />
      <TeamsList v-else :tournament="tournament" @fetch-tournament="fetchTournament" />
    </div>

    <div class="w-full py-5" v-if="activeTab === 'Qualifiers'">
      <div
        class="flex justify-between items-center"
        v-if="tournament.current_stage === 'qualifiers'"
      >
        <button
          class="flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 hover:cursor-pointer"
          @click="generateNextMatch"
        >
          <span>Create Next Match</span>
        </button>

        <button
          class="flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 hover:cursor-pointer"
          @click="terminateQualifiers"
        >
          Terminate Qualifiers
        </button>
      </div>

      <div class="grid grid-cols-2 gap-4 pt-4">
        <div class="flex flex-col">
          <div class="pt-4 mb-2 pb-4 flex justify-between">
            Overview
            <div class="italic">Click on the gray columns to sort.</div>
          </div>
          <Overview :tournament="tournament" stage="qualifiers" />
        </div>
        <Matches :tournament="tournament" stage="qualifiers" @fetch-tournament="fetchTournament" />
      </div>
    </div>

    <div class="w-full py-5" v-if="activeTab === 'Finals'">
      <div class="flex justify-between items-center">
        <button
          class="flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 hover:cursor-pointer"
          @click="generateNextMatch"
        >
          <span>Create Next Match</span>
        </button>

        <button
          class="flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 hover:cursor-pointer"
        >
          Terminate Tournament
        </button>
      </div>

      <div class="grid grid-cols-2 gap-4 pt-4">
        <div class="flex flex-col">
          <div class="mb-2 pt-4 pb-4 flex justify-between">
            Overview
            <div class="italic">Click on the highlighted columns to sort</div>
          </div>
          <Overview :tournament="tournament" stage="finals" />
        </div>
        <Matches
          :tournament="tournament"
          stage="finals"
          @fetch-tournament="fetchTournament"
          :collapsible="true"
        />
      </div>
    </div>
  </div>
</template>

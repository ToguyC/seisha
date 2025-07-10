<script setup lang="ts">
import { getTournament, postTournamentMatch, postTournamentStage } from '@/api/tournament'
import Breadcrumb from '@/components/Breadcrumb.vue'
import Overview from '@/components/Overview.vue'
import ArchersList from '@/components/single-tournament/ArchersList.vue'
import SingleTournamentHeader from '@/components/single-tournament/Header.vue'
import Matches from '@/components/single-tournament/Matches.vue'
import TeamsList from '@/components/single-tournament/TeamsList.vue'
import {
  MatchFormat,
  TournamentFormat,
  TournamentStage,
  TournamentStageName,
  TournamentStatus,
} from '@/models/constants'
import { dummyTournamentWithRelations } from '@/models/dummy'
import type {
  Archer,
  ArcherWithTournamentData,
  Team,
  TournamentWithRelations,
} from '@/models/models'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

type WithHitCount<T> = T & { hit_count: number[] }

const route = useRoute()

const tournament = ref<TournamentWithRelations>(dummyTournamentWithRelations)
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
const tabs = ref({
  participants: 'Participants',
  [TournamentStage.QUALIFIERS]: TournamentStageName.qualifiers,
  [TournamentStage.QUALIFIERS_TIE_BREAK]: TournamentStageName.qualifiers_tie_break,
  [TournamentStage.FINALS]: TournamentStageName.finals,
  [TournamentStage.FINALS_TIE_BREAK]: TournamentStageName.finals_tie_break,
})
const activeTab = ref<keyof typeof tabs.value>('participants')
const activeTabLabel = computed(() => tabs.value[activeTab.value])

const useEnkin = ref(false)
const showOverviewDetails = ref(false)

const isParticipantArcher = (participant: WithHitCount<Team | ArcherWithTournamentData>) => {
  return 'archer' in participant
}

const fetchTournament = (tournamentId: number) => {
  getTournament(tournamentId)
    .then((res) => {
      tournament.value = res.data
      document.title = `${tournament.value.name} - Seisha`

      if (tournament.value.status !== TournamentStatus.UPCOMING) {
        activeTab.value = tournament.value.current_stage
      }

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
    tournament.current_stage === TournamentStage.FINALS &&
    tournament.matches.filter((m) => m.stage === TournamentStage.QUALIFIERS).length == 0
  )
}

const generateNextMatch = () => {
  let matchFormat = MatchFormat.STANDARD

  if (
    tournament.value.current_stage === TournamentStage.QUALIFIERS_TIE_BREAK ||
    tournament.value.current_stage === TournamentStage.FINALS_TIE_BREAK
  ) {
    matchFormat = MatchFormat.IZUME
  }

  if (useEnkin.value) {
    matchFormat = MatchFormat.ENKIN
  }

  postTournamentMatch(tournament.value.id, matchFormat)
    .then((res) => {
      fetchTournament(tournament.value.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const getHitCount = (archer: Archer, stage: TournamentStage) => {
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

const getTeamHitCount = (team: Team, stage: TournamentStage) => {
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

const terminateStage = () => {
  if (
    !confirm(
      'Are you sure you want to terminate the stage? This will end all rounds for this stage. This action cannot be undone.',
    )
  ) {
    return
  }

  let sortedParticipants: WithHitCount<Team | ArcherWithTournamentData>[] = []

  if (tournament.value.format === 'individual') {
    sortedParticipants = tournament.value.archers
      .map((archer) => ({
        ...archer,
        hit_count: getHitCount(archer.archer, TournamentStage.QUALIFIERS),
      }))
      .sort((a, b) => b.hit_count[0] - a.hit_count[0])
  } else {
    sortedParticipants = tournament.value.teams
      .map((team) => ({
        ...team,
        hit_count: getTeamHitCount(team, TournamentStage.QUALIFIERS),
      }))
      .sort((a, b) => b.hit_count[0] - a.hit_count[0])
  }

  const cutoffIndex = tournament.value.advancing_count ? tournament.value.advancing_count - 1 : -1
  const cutoffHitCount = sortedParticipants[cutoffIndex]?.hit_count[0] ?? -1

  const advancingParticipants = sortedParticipants.filter((p) => p.hit_count[0] >= cutoffHitCount)
  const isTieBreakerNeeded = advancingParticipants.length > (tournament.value.advancing_count || 0)

  const advancingHits = advancingParticipants.map((p) => {
    return {
      id: isParticipantArcher(p) ? p.archer.id : p.id,
      hit_count: p.hit_count[0],
    }
  })

  postTournamentStage(tournament.value.id, advancingHits, isTieBreakerNeeded)
    .then((res) => {
      fetchTournament(tournament.value.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const terminateTieBreak = () => {
  if (
    !confirm(
      'Are you sure you want to terminate the tie-break? This will end all tie-break rounds. This action cannot be undone.',
    )
  ) {
    return
  }
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
        '!border-b-amaranth-400 !text-amaranth-400': activeTab === 'participants',
      }"
      @click="activeTab = 'participants'"
    >
      {{ tabs['participants'] }}
    </div>
    <div
      class="px-2 py-4 border-b-2 border-white text-gray-600 font-medium hover:border-b-gray-400 hover:cursor-pointer hover:text-black"
      :class="{
        '!border-b-amaranth-400 !text-amaranth-400': activeTab === TournamentStage.QUALIFIERS,
      }"
      @click="activeTab = TournamentStage.QUALIFIERS"
      v-if="!isTournamentOnlyFinals(tournament)"
    >
      {{ tabs[TournamentStage.QUALIFIERS] }}
    </div>
    <div
      class="px-2 py-4 border-b-2 border-white text-gray-600 font-medium hover:border-b-gray-400 hover:cursor-pointer hover:text-black"
      :class="{
        '!border-b-amaranth-400 !text-amaranth-400':
          activeTab === TournamentStage.QUALIFIERS_TIE_BREAK,
      }"
      @click="activeTab = TournamentStage.QUALIFIERS_TIE_BREAK"
      v-if="
        !isTournamentOnlyFinals(tournament) &&
        tournament.current_stage === TournamentStage.QUALIFIERS_TIE_BREAK
      "
    >
      {{ tabs[TournamentStage.QUALIFIERS_TIE_BREAK] }}
    </div>
    <div
      class="px-2 py-4 border-b-2 border-white text-gray-600 font-medium hover:border-b-gray-400 hover:cursor-pointer hover:text-black"
      :class="{
        '!border-b-amaranth-400 !text-amaranth-400': activeTab === TournamentStage.FINALS,
      }"
      @click="activeTab = TournamentStage.FINALS"
      v-if="tournament.current_stage === TournamentStage.FINALS"
    >
      {{ tabs[TournamentStage.FINALS] }}
    </div>
    <div
      class="px-2 py-4 border-b-2 border-white text-gray-600 font-medium hover:border-b-gray-400 hover:cursor-pointer hover:text-black"
      :class="{
        '!border-b-amaranth-400 !text-amaranth-400': activeTab === TournamentStage.FINALS_TIE_BREAK,
      }"
      @click="activeTab = TournamentStage.FINALS_TIE_BREAK"
      v-if="tournament.current_stage === TournamentStage.FINALS_TIE_BREAK"
    >
      {{ tabs[TournamentStage.FINALS_TIE_BREAK] }}
    </div>
  </div>

  <div class="flex">
    <div class="w-full py-5" v-if="activeTab === 'participants'">
      <ArchersList
        v-if="tournament.format === 'individual'"
        :tournament="tournament"
        @fetch-tournament="fetchTournament"
      />
      <TeamsList v-else :tournament="tournament" @fetch-tournament="fetchTournament" />
    </div>

    <div class="w-full py-5 grid grid-cols-1 gap-12" v-if="activeTab !== 'participants'">
      <div class="flex flex-col">
        <div class="text-2xl font-semibold mb-5 flex justify-between">
          Overview

          <div class="flex items-start">
            <div class="flex items-center h-5">
              <input
                id="show-overview-details"
                type="checkbox"
                class="w-4 h-4 border border-gray-300 rounded-sm bg-gray-50 focus:ring-3 focus:ring-blue-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800"
                required
                v-model="showOverviewDetails"
              />
            </div>
            <label
              for="show-overview-details"
              class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300"
            >
              Show Details
            </label>
          </div>
        </div>
        <Overview
          :tournament="tournament"
          :stage="activeTab"
          :allow-sorting="true"
          :show-details="showOverviewDetails"
        />
      </div>

      <div class="flex flex-col gap-5">
        <div class="text-2xl font-semibold">Matches</div>

        <div
          class="flex justify-between items-center"
          v-if="tournament.current_stage === activeTab"
        >
          <button
            class="flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-blue-700 text-white rounded hover:bg-blue-800 hover:cursor-pointer"
            @click="generateNextMatch"
          >
            <span>Create Next Match</span>
          </button>

          <button
            class="flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 hover:cursor-pointer"
            @click="terminateStage"
          >
            Terminate {{ activeTabLabel }}
          </button>
        </div>

        <Matches :tournament="tournament" :stage="activeTab" @fetch-tournament="fetchTournament" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getTournament, postTournamentMatch, putTournamentStage } from '@/api/tournament'
import Breadcrumb from '@/components/Breadcrumb.vue'
import Modal from '@/components/Modal.vue'
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
import { CheckIcon } from '@heroicons/vue/16/solid'
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
  summary: 'Summary',
})
const activeTab = ref<keyof typeof tabs.value>('participants')
const activeTabLabel = computed(() => tabs.value[activeTab.value])

const showOverviewDetails = ref(false)
const showIzumeChoiceModal = ref(false)

const izumeParticipants = ref<Record<number, boolean>>({})

const isParticipantArcher = (participant: WithHitCount<Team | ArcherWithTournamentData>) => {
  return 'archer' in participant
}

const fetchTournament = (tournamentId: number) => {
  getTournament(tournamentId)
    .then((res) => {
      tournament.value = res.data
      document.title = `${tournament.value.name} - Seisha`

      izumeParticipants.value = Object.assign(
        {},
        ...(tournament.value.format === TournamentFormat.INDIVIDUAL
          ? tournament.value.archers.map((a) => ({ [a.archer.id]: false }))
          : tournament.value.teams.map((t) => ({ [t.id]: false }))),
      )

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
  const participants: number[] = []

  if (
    tournament.value.current_stage === TournamentStage.QUALIFIERS_TIE_BREAK ||
    tournament.value.current_stage === TournamentStage.FINALS_TIE_BREAK
  ) {
    participants.push(
      ...Object.entries(izumeParticipants.value)
        .filter(([, value]) => value)
        .map(([key]) => Number(key)),
    )
  }

  postTournamentMatch(tournament.value.id, participants)
    .then((res) => {
      showIzumeChoiceModal.value = false
      izumeParticipants.value = {}
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

const advancingBasedOnHits = (participants: WithHitCount<Team | ArcherWithTournamentData>[]) => {
  return participants.map((p) => ({
    id: isParticipantArcher(p) ? p.archer.id : p.id,
    hit_count: p.hit_count[0],
  }))
}

const advancingEnkin = (participants: WithHitCount<ArcherWithTournamentData>[]) => {
  const enkinMatch = tournament.value.matches
    .filter((m) => m.stage === activeTab.value)
    .filter((m) => m.format === MatchFormat.ENKIN)

  return participants.map((p) => {
    const enkinSeries = enkinMatch.flatMap((m) => m.series).find((s) => s.archer.id === p.archer.id)
    const place = enkinSeries ? JSON.parse(enkinSeries.arrows_raw)[0] : -1

    return {
      id: p.archer.id,
      hit_count: participants.length - place,
    }
  })
}

const calculateAdvancingParticipants = (
  sortedParticipants: WithHitCount<Team | ArcherWithTournamentData>[],
  advancingCount: number,
): {
  advancingHits: { id: number; hit_count: number }[]
  isTieBreakerNeeded: boolean
} => {
  const cutoffIndex = advancingCount > 0 ? advancingCount - 1 : -1
  const cutoffHitCount = sortedParticipants[cutoffIndex]?.hit_count[0] ?? -1

  const advancingParticipants = sortedParticipants.filter((p) => p.hit_count[0] >= cutoffHitCount)
  const isTieBreakerNeeded = advancingParticipants.length > advancingCount
  const advancingHits = advancingBasedOnHits(advancingParticipants)

  return { advancingHits, isTieBreakerNeeded }
}

const calculateTieBreakWinners = (
  sortedParticipants: WithHitCount<Team | ArcherWithTournamentData>[],
  tournament: TournamentWithRelations,
): {
  advancingHits: { id: number; hit_count: number }[]
  isTieBreakerNeeded: boolean
} => {
  const getPlace = (participant: Team | ArcherWithTournamentData, stage: TournamentStage) =>
    stage === TournamentStage.QUALIFIERS_TIE_BREAK
      ? participant.qualifiers_place
      : participant.finals_place

  const stage = tournament.current_stage

  const slotsTaken =
    tournament.format === TournamentFormat.INDIVIDUAL
      ? tournament.archers.filter((a) => getPlace(a, stage) !== null).length
      : tournament.teams.filter((t) => getPlace(t, stage) !== null).length
  const slotsLeft = tournament.advancing_count ? tournament.advancing_count - slotsTaken : 0

  sortedParticipants = sortedParticipants.slice(0, slotsLeft)

  let advancingHits: { id: number; hit_count: number }[] = []

  if (tournament.current_stage === TournamentStage.QUALIFIERS_TIE_BREAK) {
    if (tournament.format === TournamentFormat.INDIVIDUAL) {
      advancingHits = advancingEnkin(sortedParticipants as WithHitCount<ArcherWithTournamentData>[])
    } else {
      advancingHits = advancingBasedOnHits(sortedParticipants)
    }
  }

  return { advancingHits, isTieBreakerNeeded: false }
}

const terminateStage = () => {
  if (
    !confirm(
      'Are you sure you want to terminate the stage? This will end all rounds for this stage. This action cannot be undone.',
    )
  ) {
    return
  }

  const { format, current_stage, archers, teams, id, advancing_count } = tournament.value

  let sortedParticipants: WithHitCount<Team | ArcherWithTournamentData>[] = (
    format === TournamentFormat.INDIVIDUAL
      ? archers.map((archer) => ({
          ...archer,
          hit_count: getHitCount(archer.archer, activeTab.value as TournamentStage),
        }))
      : teams.map((team) => ({
          ...team,
          hit_count: getTeamHitCount(team, activeTab.value as TournamentStage),
        }))
  ).sort((a, b) => b.hit_count[0] - a.hit_count[0])

  if (tournament.value.current_stage === TournamentStage.QUALIFIERS_TIE_BREAK) {
    sortedParticipants = sortedParticipants.filter((p) => p.tie_break_qualifiers)
  } else if (tournament.value.current_stage === TournamentStage.FINALS_TIE_BREAK) {
    sortedParticipants = sortedParticipants.filter((p) => p.tie_break_finals)
  } else if (tournament.value.current_stage === TournamentStage.FINALS) {
    sortedParticipants = sortedParticipants.filter((p) => p.qualifiers_place !== null)
  }

  const { advancingHits, isTieBreakerNeeded } = [
    TournamentStage.QUALIFIERS,
    TournamentStage.FINALS,
  ].includes(current_stage)
    ? calculateAdvancingParticipants(sortedParticipants, advancing_count || 0)
    : calculateTieBreakWinners(sortedParticipants, tournament.value)

  putTournamentStage(id, advancingHits, isTieBreakerNeeded)
    .then(() => fetchTournament(id))
    .catch((err) => console.error(err.message))
}

const nextMatch = () => {
  if (
    tournament.value.format === TournamentFormat.TEAM &&
    [TournamentStage.QUALIFIERS_TIE_BREAK, TournamentStage.FINALS_TIE_BREAK].includes(
      tournament.value.current_stage,
    )
  ) {
    showIzumeChoiceModal.value = true
  } else {
    generateNextMatch()
  }
}

const getIzumeParticipants = () => {
  const allParticipants: (Team | ArcherWithTournamentData)[] =
    tournament.value.format === TournamentFormat.INDIVIDUAL
      ? tournament.value.archers
      : tournament.value.teams

  const participants = allParticipants.filter((p) => {
    if (tournament.value.current_stage === TournamentStage.QUALIFIERS_TIE_BREAK) {
      return p.tie_break_qualifiers
    } else if (tournament.value.current_stage === TournamentStage.FINALS_TIE_BREAK) {
      return p.tie_break_finals
    }
    return false
  })

  if (tournament.value.format === TournamentFormat.INDIVIDUAL) {
    return (participants as ArcherWithTournamentData[]).map((a) => a.archer)
  } else {
    return participants as Team[]
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
      v-if="!isTournamentOnlyFinals(tournament) && tournament.had_qualifiers_tie_break"
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
    <div
      class="px-2 py-4 border-b-2 border-white text-gray-600 font-medium hover:border-b-gray-400 hover:cursor-pointer hover:text-black"
      :class="{
        '!border-b-amaranth-400 !text-amaranth-400': activeTab === 'summary',
      }"
      @click="activeTab = 'summary'"
      v-if="tournament.status === TournamentStatus.FINISHED"
    >
      {{ tabs['summary'] }}
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

    <div class="w-full py-5" v-else-if="activeTab === 'summary'">Place overall summary here.</div>

    <div class="w-full py-5 grid grid-cols-1 gap-12" v-else>
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
            @click="nextMatch"
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

  <Modal v-model="showIzumeChoiceModal" title="Choose Izume Participants *">
    <form class="w-full flex flex-col gap-4">
      <label
        :for="`participate-${participant.id}`"
        class="w-full py-3 px-2 text-lg flex items-center gap-5 border rounded-lg hover:cursor-pointer"
        :class="{
          'border hover:bg-gray-100': !izumeParticipants[participant.id],
          'border-blue-500 text-white bg-blue-500 hover:bg-blue-600':
            izumeParticipants[participant.id],
        }"
        v-for="participant in getIzumeParticipants()"
      >
        <input
          :id="`participate-${participant.id}`"
          type="checkbox"
          class="w-4 h-4 hidden"
          v-model="izumeParticipants[participant.id]"
        />

        <div class="w-full">
          {{ participant.name }}
        </div>
      </label>
    </form>

    <p class="italic mt-4">*By default, all the participants are to be included.</p>

    <template #footer>
      <div class="wf-full flex justify-between items-center gap-4">
        <button
          class="w-1/2 flex items-center text-sm justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
          @click="generateNextMatch"
        >
          <CheckIcon class="w-6 h-6" /> Generate Match
        </button>
        <button
          class="w-1/2 px-4 py-2 mr-2 text-sm text-gray-900 bg-white border border-gray-200 rounded hover:bg-gray-100 hover:cursor-pointer hover:text-blue-700"
          @click="showIzumeChoiceModal = false"
        >
          Discard
        </button>
      </div>
    </template>
  </Modal>
</template>

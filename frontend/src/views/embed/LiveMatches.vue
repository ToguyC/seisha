<script setup lang="ts">
import { getAllLiveTournaments, getTournament } from '@/api/tournament'
import Match from '@/components/Match.vue'
import type { TournamentWithRelations, Match as MatchModel } from '@/models/models'
import { ws } from '@/plugins/sockets'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/16/solid'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
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
const currentMatch = ref<MatchModel | null>(null)
const currentMatchIdx = ref(route.params.matchIdx ? Number(route.params.matchIdx) : 0)

const getUnfinishedMatches = (tournament: TournamentWithRelations) => {
  return tournament.matches.filter((m) => !m.finished)
}

const fetchTournament = (tournamentId: number) => {
  getTournament(tournamentId)
    .then((res) => {
      tournament.value = res.data
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const previousMatch = () => {
  const previousMatchIdx = Math.max(0, currentMatchIdx.value - 1)

  router
    .push({
      name: 'embed-live-matches',
      params: {
        id: tournament.value.id,
        matchIdx: previousMatchIdx,
      },
    })
    .then(() => {
      currentMatchIdx.value = previousMatchIdx
    })
}

const nextMatch = () => {
  const nextMatchIdx = Math.min(
    getUnfinishedMatches(tournament.value).length - 1,
    currentMatchIdx.value + 1,
  )

  router
    .push({
      name: 'embed-live-matches',
      params: {
        id: tournament.value.id,
        matchIdx: nextMatchIdx,
      },
    })
    .then(() => {
      currentMatchIdx.value = nextMatchIdx
    })
}

onMounted(() => {
  const tournamentId = Number(route.params.id)

  ws.onmessage = (ev: MessageEvent) => {
    const data = JSON.parse(ev.data)

    if (['new arrow', 'new match', 'arrow update', 'match finished'].includes(data.event)) {
      fetchTournament(tournamentId)
    }
  }

  fetchTournament(tournamentId)
})
</script>

<template>
  <div class="w-full flex flex-col justify-center gap-6">
    <Match
      v-if="currentMatch = getUnfinishedMatches(tournament)[currentMatchIdx]"
      :match="currentMatch"
      :tournament="tournament"
      :readonly="true"
      :key="currentMatch.id"
    />
    <div class="flex justify-center items-center gap-6 mt-36">
      <button
        class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 hover:cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 hover:disabled:bg-gray-200"
        @click="previousMatch()"
        :disabled="currentMatchIdx === 0"
      >
        <ChevronLeftIcon class="w-5 h-5" />
      </button>
      <div>{{ currentMatchIdx + 1 }} / {{ getUnfinishedMatches(tournament).length }}</div>
      <button
        class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 hover:cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 hover:disabled:bg-gray-200"
        @click="nextMatch()"
        :disabled="currentMatchIdx >= getUnfinishedMatches(tournament).length - 1"
      >
        <ChevronRightIcon class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

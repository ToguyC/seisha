<script setup lang="ts">
import { getAllLiveTournaments } from '@/api/tournament'
import Match from '@/components/Match.vue'
import type { TournamentWithRelations, Match as MatchModel } from '@/models/models'
import { ws } from '@/plugins/sockets'
import { onMounted, ref } from 'vue'

const liveTournaments = ref<TournamentWithRelations[]>([])
const lastMatch = ref<MatchModel | null>(null)

const getUnfinishedMatches = (tournament: TournamentWithRelations) => {
  return tournament.matches.filter((m) => !m.finished)
}

const getLastMatch = (tournament: TournamentWithRelations) => {
  const matches = tournament.matches
  return matches.length > 0 ? matches[matches.length - 1] : null
}

const fetchLiveTournaments = () => {
  getAllLiveTournaments()
    .then((res) => {
      liveTournaments.value = res.data
    })
    .catch((error) => {
      console.error('Error fetching tournaments:', error)
    })
}

onMounted(() => {
  ws.onmessage = (ev: MessageEvent) => {
    const data = JSON.parse(ev.data)

    if (['new arrow', 'new match', 'arrow update', 'match finished'].includes(data.event)) {
      fetchLiveTournaments()
    }
  }

  fetchLiveTournaments()
})
</script>

<template>
  <div class="w-full flex flex-col items-center justify-center gap-6">
    <div class="text-3xl font-bold uppercase">Live tournaments</div>

    <div class="flex flex-col divide-y divide-gray-500">
      <div class="py-10 flex flex-col gap-4" v-for="tournament in liveTournaments">
        <div class="text-xl font-semibold">{{ tournament.name }}</div>

        <Match
          v-for="match of getUnfinishedMatches(tournament)"
          :match="match"
          :tournament="tournament"
          :readonly="true"
          :key="match.id"
        />
        <div
          class="flex flex-col justify-center items-center gap-4"
          v-if="getUnfinishedMatches(tournament).length === 0"
        >
          <p class="text-xl">Last played match</p>
          <Match
            v-if="lastMatch = getLastMatch(tournament)"
            :match="lastMatch"
            :tournament="tournament"
            :readonly="true"
            :key="getLastMatch(tournament)?.id"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { deleteMatch as _deleteMatch } from '@/api/match'
import type { TournamentWithRelations } from '@/models/models'
import { TrashIcon } from '@heroicons/vue/16/solid'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { computed } from 'vue'
import Match from '../Match.vue'

const { tournament, stage } = defineProps<{
  tournament: TournamentWithRelations
  stage: string
}>()

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const fetchTournament = () => {
  emit('fetchTournament', tournament.id)
}

const matches = computed(() => {
  return tournament.matches.filter((match) => match.stage === stage)
})

const matchContainsUnknowns = (matchId: number) => {
  const match = matches.value.find((m) => m.id === matchId)
  if (!match) return false

  return match.series.some((s) => {
    const arrows = JSON.parse(s.arrows_raw) as number[]
    return arrows.some((a) => a === 2)
  })
}

const deleteMatch = (matchId: number) => {
  if (!confirm('Are your sure you want to delete this match?')) {
    return
  }

  _deleteMatch(matchId)
    .then((res) => {
      fetchTournament()
    })
    .catch((err) => {
      console.error(err.message)
    })
}
</script>

<template>
  <div class="flex flex-col divide-y divide-gray-500">
    <div v-for="match in matches" class="py-8 gap-4 flex flex-col">
      <div class="w-full grid grid-cols-3 items-center">
        <div class="w-full">
          Match created at
          {{
            new Date(match.created_at).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              hour12: false,
            })
          }}
          <div
            v-if="matchContainsUnknowns(match.id)"
            class="flex items-center gap-2 text-orange-500"
          >
            <ExclamationTriangleIcon class="w-5 h-5" /> Unknowns still presents
          </div>
        </div>

        <div class="w-full flex justify-center">
          <span v-if="match.finished" class="text-blue-600 font-semibold text-lg">Finished</span>
          <span v-else class="text-red-600 font-semibold text-lg">Live</span>
        </div>
        <div class="w-full flex justify-end">
          <button
            class="w-20 py-2 flex items-center text-sm font-semibold justify-center bg-red-100 text-red-700 rounded hover:bg-red-200 hover:cursor-pointer"
            @click="deleteMatch(match.id)"
            v-if="tournament.current_stage === stage"
          >
            <TrashIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <Match :match="match" :tournament="tournament" @fetch-tournament="fetchTournament" />
    </div>
  </div>
</template>

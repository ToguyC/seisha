<script setup lang="ts">
import { deleteMatch as _deleteMatch } from '@/api/match'
import { postTournamentMatch } from '@/api/tournament'
import type { TournamentWithRelations } from '@/models/models'
import { TrashIcon } from '@heroicons/vue/16/solid'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import Match from '../Match.vue'

const { tournament } = defineProps<{
  tournament: TournamentWithRelations
}>()

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const fetchTournament = () => {
  emit('fetchTournament', tournament.id)
}

const newMatchError = ref(false)
const newMatchErrorMessage = ref('')
const deleteMatchToggle = ref(false)

const generateNextMatch = () => {
  postTournamentMatch(tournament.id)
    .then((res) => {
      fetchTournament()
    })
    .catch((err) => {
      newMatchError.value = true
      newMatchErrorMessage.value = err.response.data.detail

      setTimeout(() => {
        newMatchError.value = false
        newMatchErrorMessage.value = ''
      }, 3000)
    })
}

const matchContainsUnknowns = (matchId: number) => {
  const match = tournament.matches.find((m) => m.id === matchId)
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
      deleteMatchToggle.value = false
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.ctrlKey) {
    deleteMatchToggle.value = true
  }
}

const handleKeyup = (event: KeyboardEvent) => {
  if (!event.ctrlKey) {
    deleteMatchToggle.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('keyup', handleKeyup)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('keyup', handleKeyup)
})
</script>

<template>
  <div>
    <div class="text-3xl text-red-500 font-bold">
      予選順位 (classement aux qualifs)<br />Ajouter la création de match enkin et mort subite + les
      phases finales et gagnants
    </div>

    <div class="flex items-center justify-between mb-6">
      <div class="text-xl font-bold text-gray-900 capitalize">
        Matches
      </div>
      <div class="flex items-center gap-4">
        <div class="text-red-500">{{ newMatchErrorMessage }}</div>
        <div class="relative">
          <div
            class="absolute animate-ping w-full h-full bg-orange-200 top-0 left-0 rounded"
            :class="{
              hidden: !newMatchError,
              block: newMatchError,
            }"
          ></div>
          <button
            class="relative w-30 flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 hover:cursor-pointer disabled:cursor-not-allowed"
            :class="{
              '!bg-orange-100 !text-orange-700': newMatchError,
            }"
            :disabled="newMatchError"
            @click="generateNextMatch"
          >
            <span v-if="!newMatchError">Next Match</span>
            <span v-else>Error</span>
          </button>
        </div>
      </div>
    </div>

    <div class="flex flex-col divide-y divide-gray-500">
      <div v-for="match in tournament.matches" class="py-8 gap-4 flex flex-col">
        <div class="w-full flex justify-between items-center">
          <div>
            <div
              v-if="matchContainsUnknowns(match.id)"
              class="flex items-center gap-2 text-orange-500"
            >
              <ExclamationTriangleIcon class="w-5 h-5" /> Unknowns still presents
            </div>
          </div>

          <button
            class="w-20 py-2 flex items-center text-sm font-semibold justify-center bg-red-100 text-red-700 rounded hover:bg-red-200 hover:cursor-pointer"
            @click="deleteMatch(match.id)"
          >
            <TrashIcon class="w-5 h-5" />
          </button>
        </div>

        <Match :match="match" :tournament="tournament" @fetch-tournament="fetchTournament" />
      </div>
    </div>
  </div>
</template>

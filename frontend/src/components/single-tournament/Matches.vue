<script setup lang="ts">
import { deleteMatch as _deleteMatch, finishMatch as _finishMatch } from '@/api/match'
import type { TournamentWithRelations } from '@/models/models'
import { ChevronDownIcon, TrashIcon } from '@heroicons/vue/16/solid'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { computed, ref } from 'vue'
import Match from '../Match.vue'
import { MatchFormat } from '@/models/constants'

const { tournament, stage } = defineProps<{
  tournament: TournamentWithRelations
  stage: string
}>()

const finishedCollapsed = ref(true)
const liveCollapsed = ref(false)

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

const finishMatch = (matchId: number) => {
  if (!confirm('Are your sure you want to finish this match?')) {
    return
  }

  _finishMatch(matchId)
    .then((res) => {
      fetchTournament()
    })
    .catch((err) => {
      console.error(err.message)
    })
}
</script>

<template>
  <div class="flex flex-col">
    <div>
      <div
        class="p-2 font-semibold flex items-center justify-between py-4 cursor-pointer"
        :class="!finishedCollapsed ? 'bg-gray-200 hover:bg-gray-300' : 'border border-gray-200'"
        @click="finishedCollapsed = !finishedCollapsed"
      >
        Finished matches
        <ChevronDownIcon
          class="w-5 h-5 transition-transform"
          :class="finishedCollapsed ? '' : 'rotate-180'"
        />
      </div>

      <div v-if="!finishedCollapsed" class="flex flex-col gap-4 border border-gray-200 p-4">
        <div v-for="match in matches.filter((m) => m.finished)" :key="match.id">
          <div class="w-full grid grid-cols-2 items-center mb-4">
            <div class="w-full">
              Match created at
              {{
                new Date(match.created_at).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false,
                })
              }}
            </div>

            <div class="w-full flex justify-end gap-4">
              <button
                class="w-20 py-2 flex items-center text-sm font-semibold justify-center bg-red-100 text-red-700 rounded hover:bg-red-200 hover:cursor-pointer"
                @click="deleteMatch(match.id)"
                v-if="tournament.current_stage === stage"
              >
                <TrashIcon class="w-5 h-5" />
              </button>
            </div>
          </div>

          <Match
            :match="match"
            :tournament="tournament"
            :readonly="true"
            @fetch-tournament="fetchTournament"
          />
        </div>
      </div>
    </div>

    <div>
      <div
        class="p-2 font-semibold flex items-center justify-between py-4 cursor-pointer"
        :class="!liveCollapsed ? 'bg-gray-200 hover:bg-gray-300' : 'border border-gray-200'"
        @click="liveCollapsed = !liveCollapsed"
      >
        Live matches
        <ChevronDownIcon
          class="w-5 h-5 transition-transform"
          :class="liveCollapsed ? '' : 'rotate-180'"
        />
      </div>

      <div v-if="!liveCollapsed" class="flex flex-col gap-4 border border-gray-200 p-4">
        <div v-for="match in matches.filter((m) => !m.finished)" :key="match.id">
          <div class="w-full grid grid-cols-2 items-center mb-4">
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
                v-if="match.format !== MatchFormat.ENKIN && matchContainsUnknowns(match.id)"
                class="flex items-center gap-2 text-orange-500"
              >
                <ExclamationTriangleIcon class="w-5 h-5" /> Unknowns still presents
              </div>
            </div>

            <div class="w-full flex justify-end gap-4">
              <button
                class="w-20 py-2 flex items-center text-sm font-semibold justify-center bg-orange-100 text-orange-700 rounded hover:bg-orange-200 hover:cursor-pointer"
                @click="finishMatch(match.id)"
                v-if="tournament.current_stage === stage && !match.finished"
              >
                Terminate
              </button>
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
    </div>
  </div>
</template>

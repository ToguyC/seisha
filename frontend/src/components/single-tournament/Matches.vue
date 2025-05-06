<script setup lang="ts">
import { getArrow, postArrowToMatch, putArrow, deleteMatch as _deleteMatch } from '@/api/match'
import { postTournamentMatch } from '@/api/tournament'
import type { Archer, Match as MatchModel, TournamentWithRelations } from '@/models/models'
import { ArrowRightIcon, HashtagIcon, PlusIcon, TrashIcon } from '@heroicons/vue/16/solid'
import { computed, ref } from 'vue'

const { tournament } = defineProps<{
  tournament: TournamentWithRelations
}>()

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const fetchTournament = () => {
  emit('fetchTournament', tournament.id)
}

const mouseHoverArrow = ref<{ match: number; archer: number; arrow: number } | null>(null)

const isIndividual = computed(() => {
  console.log(tournament)
  return tournament.format === 'individual'
})

const isMouseHoveringCell = (match: MatchModel, archer: Archer, arrowIndex: number) => {
  return (
    mouseHoverArrow.value !== null &&
    mouseHoverArrow.value.match === match.id &&
    mouseHoverArrow.value.archer === archer.id &&
    mouseHoverArrow.value.arrow === arrowIndex
  )
}

const generateNextMatch = () => {
  postTournamentMatch(tournament.id)
    .then((res) => {
      fetchTournament()
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const getSeriesMaxArrows = (match: MatchModel) => {
  // TODO: need to change based on match.type (standard, enkin, mort subite).
  // Enkin is a special case where the number of max arrows is undefined. Maybe, change the UI to have an incremental table (add a column for each arrow).
  // Mort subite is simply 1 arrow, but I don't know the definitive match type name.
  // For now, I will just return 4 arrows for all match types.
  return 4
}

const remainingArrows = (match: MatchModel, archer: Archer) => {
  const seriesArrows = getArcherSeriesArrows(match, archer)
  const maxArrows = getSeriesMaxArrows(match)

  return maxArrows - seriesArrows.length
}

const getArcherNumber = (archer: Archer) => {
  if (isIndividual.value) {
    return tournament.archers.find((a) => a.archer.id === archer.id)?.number || 0
  }

  const team = getArcherTeam(archer)
  return team?.archers.find((a) => a.archer.id === archer.id)?.number || 0
}

const getArcherSeriesArrows = (match: MatchModel, archer: Archer) => {
  const series = match.series.find((s) => s.archer.id === archer.id)

  return series ? (JSON.parse(series.arrows_raw) as number[]) : []
}

const getArcherTeam = (archer: Archer) => {
  return tournament.teams.find((team) => team.archers.some((a) => a.archer.id === archer.id))
}

const getArchers = (match: MatchModel) => {
  if (isIndividual.value) {
    return match.archers
  }

  // slice() to create a shallow copy of the array, avoiding in-place sorting
  const sortedByNumber = match.archers
    .slice()
    .sort((a, b) => getArcherNumber(a) - getArcherNumber(b))
  const sortedByTeam = sortedByNumber.sort((a, b) => getArcherTeam(a)!.id - getArcherTeam(b)!.id)
  return sortedByTeam
}

const shotArrow = (match: MatchModel, archer: Archer, state: number) => {
  postArrowToMatch(match.id, archer.id, state)
    .then((res) => {
      fetchTournament()
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const arrowCycleUI = (arrowState: number) => {
  switch (arrowState) {
    case 0:
      return '⨉'
    case 1:
      return '◯'
    case 2:
      return '?'
    default:
      return ''
  }
}

const setArrowState = (match: MatchModel, archer: Archer, arrowIndex: number, state: number) => {
  getArrow(match.id, archer.id, arrowIndex).then((res) => {
    putArrow(match.id, archer.id, arrowIndex, state)
      .then((res) => {
        fetchTournament()
      })
      .catch((err) => {
        console.error(err.message)
      })
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
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="text-xl font-bold text-gray-900 capitalize">Matches</div>
      <button
        class="w-30 flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 hover:cursor-pointer"
        @click="generateNextMatch"
      >
        Next Match
      </button>
    </div>

    <div class="flex flex-col gap-4">
      <div v-for="match in tournament.matches" class="flex gap-4">
        <table class="border-2">
          <thead class="text-center">
            <tr>
              <td class="border-2 w-20"></td>
              <td class="border-2 w-48"></td>
              <td class="border-2 w-40" v-if="!isIndividual"></td>
              <td class="border-2 w-40" colspan="2">予選一立目</td>
              <td class="border-2 w-40" colspan="2">予選二立目</td>
            </tr>
            <tr>
              <td class="border-2 w-20">立順</td>
              <td class="border-2 w-48">氏名</td>
              <td class="border-2 w-40" v-if="!isIndividual">チーム</td>
              <td class="border-2 w-20">甲矢</td>
              <td class="border-2 w-20">乙矢</td>
              <td class="border-2 w-20">甲矢</td>
              <td class="border-2 w-20">乙矢</td>
            </tr>
          </thead>
          <tbody class="text-center">
            <tr v-for="archer in getArchers(match)" :key="archer.id">
              <td class="border-2 w-20">{{ getArcherNumber(archer) }}</td>
              <td class="border-2 w-48">{{ archer.name }}</td>

              <td v-if="!isIndividual" class="border-2 w-40">{{ getArcherTeam(archer)?.name }}</td>
              <td
                class="border-2 w-20"
                v-for="(arr, i) in getArcherSeriesArrows(match, archer)"
                @mouseenter="mouseHoverArrow = { match: match.id, archer: archer.id, arrow: i }"
                @mouseleave="mouseHoverArrow = null"
              >
                <div class="w-full h-full">
                  <div
                    class="flex bg-orange-100 text-orange-700 font-semibold hover:cursor-pointer"
                    v-if="isMouseHoveringCell(match, archer, i)"
                  >
                    <div
                      class="w-1/2 hover:bg-orange-200 hover:text-orange-800 hover:font-bold"
                      :class="{ hidden: arr === 0 }"
                      @click="setArrowState(match, archer, i, 0)"
                    >
                      ⨉
                    </div>
                    <div
                      class="w-1/2 hover:bg-orange-200 hover:text-orange-800 hover:font-bold"
                      :class="{ hidden: arr === 1 }"
                      @click="setArrowState(match, archer, i, 1)"
                    >
                      ◯
                    </div>
                    <div
                      class="w-1/2 hover:bg-orange-200 hover:text-orange-800 hover:font-bold"
                      :class="{ hidden: arr === 2 }"
                      @click="setArrowState(match, archer, i, 2)"
                    >
                      ?
                    </div>
                  </div>
                  <div v-else class="flex justify-center items-center">{{ arrowCycleUI(arr) }}</div>
                </div>
              </td>
              <td class="border-2 w-20" v-for="i in remainingArrows(match, archer)">
                <div
                  class="w-full h-full flex items-center bg-blue-100 text-blue-700 font-semibold hover:cursor-pointer"
                  v-if="i == 1"
                >
                  <div
                    class="w-1/3 hover:text-blue-800 hover:bg-blue-200 hover:font-bold"
                    @click="shotArrow(match, archer, 0)"
                  >
                    ⨉
                  </div>
                  <div
                    class="w-1/3 hover:text-blue-800 hover:bg-blue-200 hover:font-bold"
                    @click="shotArrow(match, archer, 1)"
                  >
                    ◯
                  </div>
                  <div
                    class="w-1/3 hover:text-blue-800 hover:bg-blue-200 hover:font-bold"
                    @click="shotArrow(match, archer, 2)"
                  >
                    ?
                  </div>
                </div>
                <div v-else class=""></div>
              </td>
            </tr>
          </tbody>
        </table>

        <button
          class="w-20 flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 hover:cursor-pointer"
          @click="deleteMatch(match.id)"
        >
          <TrashIcon class="w-5 h-5" />
        </button>
      </div>
    </div>
  </div>
</template>

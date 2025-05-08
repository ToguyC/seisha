<script setup lang="ts">
import { getArrow, postArrowToMatch, putArrow } from '@/api/match'
import type { Archer, Match, Team, TournamentWithRelations } from '@/models/models'
import { computed, ref } from 'vue'

const { match, tournament, readonly } = defineProps<{
  match: Match
  tournament: TournamentWithRelations
  readonly?: boolean
}>()

const isIndividual = computed(() => tournament.format === 'individual')
const mouseHoverArrow = ref<{ match: number; archer: number; arrow: number } | null>(null)

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const fetchTournament = () => {
  emit('fetchTournament', tournament.id)
}

const isMouseHoveringCell = (match: Match, archer: Archer, arrowIndex: number) => {
  return (
    !readonly &&
    mouseHoverArrow.value !== null &&
    mouseHoverArrow.value.match === match.id &&
    mouseHoverArrow.value.archer === archer.id &&
    mouseHoverArrow.value.arrow === arrowIndex
  )
}

const getSeriesMaxArrows = (match: Match) => {
  // TODO: need to change based on match.type (standard, enkin, mort subite).
  // Enkin is a special case where the number of max arrows is undefined. Maybe, change the UI to have an incremental table (add a column for each arrow).
  // Mort subite is simply 1 arrow, but I don't know the definitive match type name.
  // For now, I will just return 4 arrows for all match types.
  return 4
}

const remainingArrows = (match: Match, archer: Archer) => {
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

const getArcherSeriesArrows = (match: Match, archer: Archer) => {
  const series = match.series.find((s) => s.archer.id === archer.id)

  return series ? (JSON.parse(series.arrows_raw) as number[]) : []
}

const getArcherTeam = (archer: Archer) => {
  return tournament.teams.find((team) => team.archers.some((a) => a.archer.id === archer.id))
}

const getTeamSize = (archer: Archer) => {
  const team = getArcherTeam(archer)
  return team ? team.archers.length : 1
}

const getArchers = (match: Match) => {
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

const shotArrow = (match: Match, archer: Archer, state: number) => {
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

const setArrowState = (match: Match, archer: Archer, arrowIndex: number, state: number) => {
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

const getTeamTotal = (team: Team, match: Match) => {
  return team.archers.reduce((total, archerWithNumber) => {
    const series = getArcherSeriesArrows(match, archerWithNumber.archer)
    return total + series.reduce((sum, arrow) => sum + Number(arrow === 1), 0)
  }, 0)
}

const getTeamUnknowns = (team: Team, match: Match) => {
  return team.archers.reduce((total, archerWithNumber) => {
    const series = getArcherSeriesArrows(match, archerWithNumber.archer)
    return total + series.reduce((sum, arrow) => sum + Number(arrow === 2), 0)
  }, 0)
}

const getArcherTotal = (archer: Archer, match: Match) => {
  const series = getArcherSeriesArrows(match, archer)
  return series.reduce((sum, arrow) => sum + Number(arrow === 1), 0)
}

const getArcherUnknowns = (archer: Archer, match: Match) => {
  const series = getArcherSeriesArrows(match, archer)
  return series.reduce((sum, arrow) => sum + Number(arrow === 2), 0)
}

const getTotalArrows = (match: Match, team: Team, archer: Archer) => {
  return isIndividual.value ? getArcherTotal(archer, match) : getTeamTotal(team, match)
}

const getTotalUnkowns = (match: Match, team: Team, archer: Archer) => {
  return isIndividual.value ? getArcherUnknowns(archer, match) : getTeamUnknowns(team, match)
}

const matchStageName = (match: Match) => {
  console.log(match.stage)
  switch (match.stage) {
    case 'qualifers':
      return '予選'
    case 'finals':
      return '決勝'
    default:
      break
  }
}
</script>

<template>
  <table class="w-full border border-separate border-spacing-0">
    <thead class="text-center">
      <tr>
        <td class="border w-20" rowspan="2" v-if="!isIndividual">
          {{ matchStageName(match) }}<br />立番号
        </td>
        <td class="border w-32" rowspan="2" v-if="!isIndividual">チーム名</td>
        <td class="border w-14" rowspan="2">立順</td>
        <td class="border w-48" rowspan="2">氏名</td>
        <td class="border w-40" colspan="2">{{ matchStageName(match) }}一立目</td>
        <td class="border w-40" colspan="2">{{ matchStageName(match) }}二立目</td>
        <td class="border w-16" rowspan="2">合計</td>
      </tr>
      <tr>
        <td class="border w-20">甲矢</td>
        <td class="border w-20">乙矢</td>
        <td class="border w-20">甲矢</td>
        <td class="border w-20">乙矢</td>
      </tr>
    </thead>
    <tbody class="text-center">
      <tr v-for="(archer, shajoPlace) in getArchers(match)" :key="archer.id">
        <td
          class="border w-20"
          :rowspan="getTeamSize(archer)"
          v-if="!isIndividual && getArcherNumber(archer) === 1"
        >
          {{ getArcherTeam(archer)?.number }}
        </td>
        <td
          class="border w-32"
          :rowspan="getTeamSize(archer)"
          v-if="!isIndividual && getArcherNumber(archer) === 1"
        >
          {{ getArcherTeam(archer)?.name }}
        </td>
        <td class="border w-14">{{ shajoPlace + 1 }}</td>
        <td class="border w-48">{{ archer.name }}</td>
        <td
          class="border w-20"
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
        <td class="border w-20" v-for="i in remainingArrows(match, archer)">
          <div
            class="w-full h-full flex items-center bg-blue-100 text-blue-700 font-semibold hover:cursor-pointer"
            v-if="i == 1 && !readonly"
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
        </td>
        <td
          class="border w-16"
          :rowspan="getTeamSize(archer)"
          v-if="(!isIndividual && getArcherNumber(archer) === 1) || isIndividual"
        >
          <div class="flex justify-center items-center gap-1">
            <div>
              {{ getTotalArrows(match, getArcherTeam(archer)!, archer) }}
            </div>
            <div v-if="getTotalUnkowns(match, getArcherTeam(archer)!, archer) > 0">
              (+{{ getTotalUnkowns(match, getArcherTeam(archer)!, archer) }}?)
            </div>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { getArrow, postArrowToMatch, putArrow } from '@/api/match'
import { HitOutcome, TournamentStage } from '@/models/constants'
import type { Archer, Match, Team, TournamentWithRelations } from '@/models/models'
import { computed, ref } from 'vue'
import ArrowIndicator from '@/components/matches/ArrowIndicator.vue'
import NewArrow from './matches/NewArrow.vue'

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

const getSeriesMaxArrows = (match: Match) => {
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

  return series ? (JSON.parse(series.arrows_raw) as HitOutcome[]) : []
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

const shotArrow = (match: Match, archer: Archer, state: HitOutcome) => {
  postArrowToMatch(match.id, archer.id, state)
    .then((res) => {
      fetchTournament()
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const setArrowOutcome = (match: Match, archer: Archer, arrowIndex: number, outcome: HitOutcome) => {
  getArrow(match.id, archer.id, arrowIndex).then((res) => {
    putArrow(match.id, archer.id, arrowIndex, outcome)
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
  switch (match.stage) {
    case TournamentStage.QUALIFIERS:
      return '予選'
    case TournamentStage.FINALS:
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
        <td class="border w-48 text-left pl-4">{{ archer.name }}</td>
        <td
          class="border w-20"
          v-for="(outcome, i) in getArcherSeriesArrows(match, archer)"
          @mouseenter="mouseHoverArrow = { match: match.id, archer: archer.id, arrow: i }"
          @mouseleave="mouseHoverArrow = null"
        >
          <ArrowIndicator
            :match="match"
            :archer="archer"
            :arrowNumber="i"
            :outcome="outcome"
            :readonly="readonly"
            :mouseHoverArrow="mouseHoverArrow"
            @setArrowOutcome="setArrowOutcome"
          ></ArrowIndicator>
        </td>
        <td class="border w-20" v-if="!readonly && remainingArrows(match, archer) > 0">
          <NewArrow :match="match" :archer="archer" @shotArrow="shotArrow"></NewArrow>
        </td>
        <td
          class="border w-20"
          v-if="remainingArrows(match, archer) > 0"
          v-for="_ in remainingArrows(match, archer) - 1"
        ></td>
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

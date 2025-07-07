<script setup lang="ts">
import { getArrow, postArrowToMatch, putArrow } from '@/api/match'
import { HitOutcome, MatchFormat, TournamentFormat, TournamentStage } from '@/models/constants'
import type { Archer, Match, Team, TournamentWithRelations } from '@/models/models'
import { computed, ref } from 'vue'
import Standard from './matches/Standard.vue'
import Izume from './matches/Izume.vue'

const { match, tournament, readonly } = defineProps<{
  match: Match
  tournament: TournamentWithRelations
  readonly?: boolean
}>()

const isIndividual = computed(() => tournament.format === 'individual')

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const fetchTournament = () => {
  emit('fetchTournament', tournament.id)
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
    return match.archers.sort((a, b) => {
      return getArcherNumber(a) - getArcherNumber(b)
    })
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
    case TournamentStage.QUALIFIERS_TIE_BREAK:
      return '予選'
    case TournamentStage.FINALS:
    case TournamentStage.FINALS_TIE_BREAK:
      return '決勝'
    default:
      break
  }
}

const getQualifiersSlotLeft = () => {
  if (tournament.advancing_count === null) {
    return 0
  }

  if (tournament.format === TournamentFormat.INDIVIDUAL) {
    const alreadyQualified = tournament.archers.filter((a) => a.qualifiers_place !== null).length

    return tournament.advancing_count - alreadyQualified
  } else {
    const alreadyQualified = tournament.teams
      .filter((t) => t.qualifiers_place !== null)
      .flatMap((t) => t.archers).length

    return tournament.advancing_count - alreadyQualified
  }
}
</script>

<template>
  <Standard
    v-if="match.format === MatchFormat.STANDARD"
    :match="match"
    :is-individual="isIndividual"
    :readonly="readonly"
    :match-stage-name="matchStageName"
    :get-archers="getArchers"
    :get-team-size="getTeamSize"
    :get-archer-number="getArcherNumber"
    :get-archer-team="getArcherTeam"
    :get-archer-series-arrows="getArcherSeriesArrows"
    :set-arrow-outcome="setArrowOutcome"
    :get-total-arrows="getTotalArrows"
    :get-total-unkowns="getTotalUnkowns"
    :shot-arrow="shotArrow"
  />
  <Izume
    v-else-if="match.format === MatchFormat.IZUME"
    :match="match"
    :is-individual="isIndividual"
    :readonly="readonly"
    :match-stage-name="matchStageName"
    :get-archers="getArchers"
    :get-team-size="getTeamSize"
    :get-archer-number="getArcherNumber"
    :get-archer-team="getArcherTeam"
    :get-archer-series-arrows="getArcherSeriesArrows"
    :set-arrow-outcome="setArrowOutcome"
    :get-total-arrows="getTotalArrows"
    :get-total-unkowns="getTotalUnkowns"
    :shot-arrow="shotArrow"
  />
</template>

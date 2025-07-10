<script setup lang="ts">
import { TournamentStage } from '@/models/constants'
import type {
  Archer,
  ArcherWithTournamentData,
  Team,
  TournamentWithRelations,
} from '@/models/models'

const { tournament, sorting, reversed, stage } = defineProps<{
  tournament: TournamentWithRelations
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
}>()

const getArchers = () => {
  const filterParticipants = (p: Team) => {
    if (stage === TournamentStage.QUALIFIERS || tournament.advancing_count === null) {
      return true
    } else if (stage === TournamentStage.QUALIFIERS_TIE_BREAK) {
      return p.tie_break_qualifiers
    } else if (stage === TournamentStage.FINALS) {
      return p.qualifiers_place !== null
    } else if (stage === TournamentStage.FINALS_TIE_BREAK) {
      return p.tie_break_finals
    }
    return false
  }

  // Team tournament sorting
  let sortedTeams = [...tournament.teams].filter(filterParticipants)
  if (sorting === 'hits') {
    sortedTeams.sort((a, b) => {
      const ratioA = getTeamHitCount(a)[2]
      const ratioB = getTeamHitCount(b)[2]
      return reversed ? ratioB - ratioA : ratioA - ratioB
    })
  } else {
    sortedTeams.sort((a, b) => {
      return reversed ? b.number - a.number : a.number - b.number
    })
  }

  // Flatten archers, always sorted by archer number within team
  return sortedTeams.flatMap((team) => {
    return [...team.archers].sort((a, b) => a.number - b.number)
  })
}

const getHitCount = (archer: Archer) => {
  const allSeries = tournament.matches
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

const getTeamHitCount = (team: Team) => {
  const { hits, total } = team.archers.reduce(
    (acc, a) => {
      const [archerHits, archerTotal] = getHitCount(a.archer)
      acc.hits += archerHits
      acc.total += archerTotal
      return acc
    },
    { hits: 0, total: 0 },
  )

  return [hits, total, hits / total || 0]
}

const getArcherTeam = (archer: Archer) => {
  return tournament.teams.find((team) => team.archers.some((a) => a.archer.id === archer.id))
}

const getTeamSize = (archer: Archer) => {
  const team = getArcherTeam(archer)
  return team ? team.archers.length : 1
}

const getArcherNumber = (archer: ArcherWithTournamentData) => {
  const team = getArcherTeam(archer.archer)
  return team?.archers.find((a) => a.archer.id === archer.archer.id)?.number || 0
}

const isQualified = (archer: ArcherWithTournamentData) => {
  const archer_team = getArcherTeam(archer.archer)
  return stage === TournamentStage.QUALIFIERS && archer_team?.qualifiers_place !== null
}

const isTieBreak = (archer: ArcherWithTournamentData) => {
  const archer_team = getArcherTeam(archer.archer)
  return (
    (stage === TournamentStage.QUALIFIERS && archer_team?.tie_break_qualifiers) ||
    (stage === TournamentStage.FINALS && archer_team?.tie_break_finals)
  )
}

const getRank = (archer: ArcherWithTournamentData) => {
  const allArchers = getArchers()

  // Get hit counts for all archers
  const archersWithHits = allArchers.map((a) => ({
    archer: a,
    hits: getHitCount(a.archer)[0],
  }))

  // Sort by hits in descending order (highest hits first)
  archersWithHits.sort((a, b) => b.hits - a.hits)

  // Find the target archer's hits
  const targetHits = getHitCount(archer.archer)[0]

  // Calculate rank with proper tie handling
  let rank = 1
  for (let i = 0; i < archersWithHits.length; i++) {
    if (archersWithHits[i].hits > targetHits) {
      rank = i + 2 // +2 because we want the rank after this group
    } else if (archersWithHits[i].hits === targetHits) {
      // Found our target or someone with same hits
      break
    }
  }

  return rank
}
</script>

<template>
  <tr
    v-for="archer in getArchers()"
    :key="archer.archer.id"
    :class="{
      'bg-emerald-500/50': isQualified(archer),
      'bg-gray-400/50': isTieBreak(archer),
      'bg-amber-400/50': stage === TournamentStage.FINALS && archer.finals_place === 1,
      'bg-slate-400/50': stage === TournamentStage.FINALS && archer.finals_place === 2,
      'bg-amber-800/50': stage === TournamentStage.FINALS && archer.finals_place === 3,
    }"
  >
    <td
      v-if="getArcherNumber(archer) === 1"
      class="border w-20"
      :rowspan="getTeamSize(archer.archer)"
    >
      {{ getArcherTeam(archer.archer)?.number }}
    </td>
    <td
      v-if="getArcherNumber(archer) === 1"
      class="border w-32"
      :rowspan="getTeamSize(archer.archer)"
    >
      {{ getArcherTeam(archer.archer)?.name }}
    </td>
    <td class="border w-20">{{ getArcherNumber(archer) }}</td>
    <td class="border w-20 text-left pl-4">{{ archer.archer.name }}</td>
    <td class="border w-16">{{ getHitCount(archer.archer)[0] }}</td>
    <td class="border w-16">{{ getHitCount(archer.archer)[1] }}</td>
    <template v-if="getArcherNumber(archer) === 1">
      <td class="border w-20" :rowspan="getTeamSize(archer.archer)">
        {{ getTeamHitCount(getArcherTeam(archer.archer)!)[0] }} /
        {{ getTeamHitCount(getArcherTeam(archer.archer)!)[1] }}
      </td>
    </template>
    <template v-if="stage !== tournament.current_stage">
      <td v-if="getArcherNumber(archer) === 1" rowspan="2" class="border w-16">
        {{ getRank(archer) }}位
      </td>
      <td v-if="getArcherNumber(archer) === 1" rowspan="2" class="border w-16">
        <span v-if="isQualified(archer)"> Qualified </span>
        <span v-if="isTieBreak(archer)"> Tie Break </span>
      </td>
    </template>
  </tr>
</template>

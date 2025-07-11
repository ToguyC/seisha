<script setup lang="ts">
import { HitOutcome, MatchFormat, TournamentStage } from '@/models/constants'
import type {
  Archer,
  ArcherWithTournamentData,
  Match,
  Team,
  TournamentWithRelations,
} from '@/models/models'
import { computed } from 'vue'

const { tournament, sorting, reversed, stage } = defineProps<{
  tournament: TournamentWithRelations
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
  allowSorting: boolean
}>()

const teamRanks = computed(() => {
  // Only consider teams that are part of the current stage
  const relevantTeams = tournament.teams.filter((team) => {
    if (stage === TournamentStage.QUALIFIERS) {
      return true
    } else if (stage === TournamentStage.QUALIFIERS_TIE_BREAK) {
      return team.qualifiers_place === null
    } else if (stage === TournamentStage.FINALS) {
      return team.qualifiers_place !== null
    }
    return false
  })

  const teamsWithHits = relevantTeams.map((team) => ({
    id: team.id,
    hits: getTeamHitCount(team)[0],
  }))

  // Sort by hits descending
  teamsWithHits.sort((a, b) => b.hits - a.hits)

  // Compute ranks with tie handling
  const ranks = new Map<number, number>()
  let currentRank = 1

  for (let i = 0; i < teamsWithHits.length; i++) {
    if (i > 0 && teamsWithHits[i].hits < teamsWithHits[i - 1].hits) {
      currentRank = i + 1
    }
    ranks.set(teamsWithHits[i].id, currentRank)
  }

  return ranks
})

const izumeRounds = computed(() => getIzumeRounds())

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
      const [archerHits, archerTotal] = getHitCount(a.archer)!
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
  return (
    [TournamentStage.QUALIFIERS_TIE_BREAK, TournamentStage.FINALS_TIE_BREAK].includes(
      stage as TournamentStage,
    ) && archer_team?.qualifiers_place !== null
  )
}

const isTieBreak = (archer: ArcherWithTournamentData) => {
  const archer_team = getArcherTeam(archer.archer)
  return (
    (stage === TournamentStage.QUALIFIERS && archer_team?.tie_break_qualifiers) ||
    (stage === TournamentStage.FINALS && archer_team?.tie_break_finals)
  )
}

const arrowCycleUI = (arrowState: HitOutcome | undefined) => {
  switch (arrowState) {
    case HitOutcome.MISS:
      return '⨉'
    case HitOutcome.HIT:
      return '◯'
    case HitOutcome.ENSURE:
      return '?'
    case undefined:
      return '-'
  }
}

const getIzumeRounds = () => {
  const matches = tournament.matches
    .filter((match) => match.stage === stage)
    .filter((match) => match.format === MatchFormat.IZUME)

  return matches
}

const getArcherHit = (archer: Archer, match: Match) => {
  const series = match.series.find((s) => s.archer.id === archer.id)
  if (!series) return undefined

  const arrows = JSON.parse(series.arrows_raw) as number[]
  return arrows[0]
}

const getTeamHits = (team: Team, match: Match) => {
  const hits = team.archers.map((a) => getArcherHit(a.archer, match))

  return hits
    .reduce((acc, hit) => {
      if (hit !== undefined) acc.push(hit)
      return acc
    }, [] as HitOutcome[])
    .reduce((total, hit) => {
      return total + Number(hit === HitOutcome.HIT)
    }, 0)
}

const archerInMatch = (archer: Archer, match: Match) => {
  return match.archers.map((a) => a.id).includes(archer.id)
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
      class="border w-10"
      :rowspan="getTeamSize(archer.archer)"
    >
      {{ getArcherTeam(archer.archer)?.number }}
    </td>
    <td
      v-if="getArcherNumber(archer) === 1"
      class="border w-16"
      :rowspan="getTeamSize(archer.archer)"
    >
      {{ getArcherTeam(archer.archer)?.name }}
    </td>
    <td class="border w-10">{{ getArcherNumber(archer) }}</td>
    <td class="border border-r-4 w-20 text-left pl-4">{{ archer.archer.name }}</td>
    <template v-if="izumeRounds.length === 0">
      <td class="border w-10">-</td>
      <td class="border w-10">-</td>
    </template>

    <template v-else>
      <template v-for="match in izumeRounds" :key="match.id">
        <td class="border w-10" v-if="archerInMatch(archer.archer, match)">
          {{ arrowCycleUI(getArcherHit(archer.archer, match)) }}
        </td>
        <td
          v-else
          class="border-l"
          :class="{
            'border-t': archer.number === 1,
            'border-b': archer.number === getTeamSize(archer.archer),
          }"
        ></td>
        <template v-if="getArcherNumber(archer) === 1">
          <td
            class="border w-10"
            :rowspan="getTeamSize(archer.archer)"
            v-if="archerInMatch(archer.archer, match)"
          >
            {{ getTeamHits(getArcherTeam(archer.archer)!, match) }} /
            {{ getArcherTeam(archer.archer)!.archers.length }}
          </td>
          <td v-else :rowspan="getTeamSize(archer.archer)" class="border-r border-t border-b"></td>
        </template>
      </template>
    </template>

    <template v-if="stage !== tournament.current_stage">
      <td v-if="getArcherNumber(archer) === 1" rowspan="2" class="border border-l-4 w-16">
        <span v-if="isQualified(archer)"> Qualified </span>
        <span v-if="isTieBreak(archer)"> Tie Break </span>
      </td>
    </template>
  </tr>
</template>

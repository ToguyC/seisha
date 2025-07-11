<script setup lang="ts">
import { HitOutcome, TournamentStage } from '@/models/constants'
import type { Archer, ArcherWithTournamentData, TournamentWithRelations } from '@/models/models'
import { computed } from 'vue'

const { tournament, sorting, reversed, stage } = defineProps<{
  tournament: TournamentWithRelations
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
  showDetails: boolean
}>()

const archerRanks = computed(() => {
  // Get all archers that will be shown
  const allArchers = getArchers()

  const archersWithHits = allArchers.map((archer) => ({
    id: archer.archer.id,
    hits: getHitCount(archer.archer)[0],
  }))

  // Sort by hits descending
  archersWithHits.sort((a, b) => b.hits - a.hits)

  const ranks = new Map<number, number>()
  let currentRank = 1

  for (let i = 0; i < archersWithHits.length; i++) {
    if (i > 0 && archersWithHits[i].hits < archersWithHits[i - 1].hits) {
      currentRank = i + 1
    }
    ranks.set(archersWithHits[i].id, currentRank)
  }

  return ranks
})

const getArchers = () => {
  const filterParticipants = (p: ArcherWithTournamentData) => {
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

  return tournament.archers.filter(filterParticipants).sort((a, b) => {
    let compare = 0

    if (sorting === 'hits') {
      const ratioA = getHitCount(a.archer)[2]
      const ratioB = getHitCount(b.archer)[2]
      compare = ratioA - ratioB
    } else {
      compare = a.archer.id - b.archer.id
    }

    return reversed ? -compare : compare
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

const getHitsPerRound = (archer: ArcherWithTournamentData, round: number) => {
  const allSeries = tournament.matches
    .filter((match) => match.stage === stage)
    .sort((a, b) => a.id - b.id)
    .flatMap((match) => match.series)
    .filter((series) => series.archer.id === archer.archer.id)

  if (allSeries[round] === undefined) {
    return [-1, -1, -1, -1]
  }

  const parsed = JSON.parse(allSeries[round].arrows_raw) as number[]
  return parsed.concat(Array(4 - parsed.length).fill(-1))
}

const getHitsPerRoundWithTotal = (archer: ArcherWithTournamentData, round: number) => {
  const hits = getHitsPerRound(archer, round)
  const total = hits.reduce((a, b) => (b === HitOutcome.HIT ? a + b : a), 0)
  return { hits, total }
}

const isQualified = (archer: ArcherWithTournamentData) => {
  return stage === TournamentStage.QUALIFIERS && archer.qualifiers_place !== null
}

const isTieBreak = (archer: ArcherWithTournamentData) => {
  return (
    (stage === TournamentStage.QUALIFIERS && archer.tie_break_qualifiers) ||
    (stage === TournamentStage.FINALS && archer.tie_break_finals)
  )
}

const arrowCycleUI = (arrowState: HitOutcome) => {
  switch (arrowState) {
    case HitOutcome.MISS:
      return '⨉'
    case HitOutcome.HIT:
      return '◯'
    case HitOutcome.ENSURE:
      return '?'
  }
}

const getRounds = () => {
  if (stage === TournamentStage.QUALIFIERS) {
    return tournament.qualifiers_round_count
  } else if (stage === TournamentStage.FINALS) {
    return tournament.finals_round_count
  }

  return 0
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
    <td class="border w-10">{{ archer.number }}</td>
    <td class="border border-r-4 w-20 text-left pl-4">{{ archer.archer.name }}</td>
    <template v-for="i in getRounds()">
      <template v-for="{ hits, total } in [getHitsPerRoundWithTotal(archer, i - 1)]">
        <td
          class="border w-8"
          :class="{
            'border-r-4': hitIdx === getRounds() - 1,
          }"
          v-if="showDetails"
          v-for="(hit, hitIdx) in hits"
        >
          {{ arrowCycleUI(hit) }}
        </td>
        <td class="border border-r-4 w-8">
          {{ total }}
        </td>
      </template>
    </template>
    <td class="border w-10 font-semibold">
      {{ getHitCount(archer.archer)[0] }}
    </td>
    <td v-if="stage !== tournament.current_stage" class="border border-l-4 w-16">
      {{ archerRanks.get(archer.archer.id) }}位
    </td>
    <td v-if="stage !== tournament.current_stage" class="border w-16">
      <span v-if="isQualified(archer)"> Qualified </span>
      <span v-if="isTieBreak(archer)"> Tie Break </span>
    </td>
  </tr>
</template>
